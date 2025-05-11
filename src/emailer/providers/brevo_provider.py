"""
Brevo Email Provider

This module implements the Brevo email provider.
"""

import asyncio
import functools
import json
from typing import Dict, Any, Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from emailer.exceptions import SendFailedError
from emailer.providers.email_provider import EmailProvider


class BrevoEmailProvider(EmailProvider):
    """Email provider for Brevo (formerly Sendinblue)."""
    
    def __init__(self, brevo_api_key: str, sender_name: str, sender_email: str,
                 initial_poll_delay: int = 2, 
                 max_poll_attempts: int = 5, 
                 poll_interval_base: int = 3):
        """Initialize the Brevo email provider."""
        super().__init__(sender_name, sender_email)
        self.api_key = brevo_api_key
        
        # Set up Brevo client configuration
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key['api-key'] = self.api_key

        self.initial_poll_delay = initial_poll_delay
        self.max_poll_attempts = max_poll_attempts
        self.poll_interval_base = poll_interval_base

    async def send(self, to_email: str, subject: str, html_content: str,
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            message_id = await self._execute_send_email_request(to_email, subject, html_content, metadata)
            
            await asyncio.sleep(self.initial_poll_delay)  # Use instance attribute
            
            return await self._poll_for_delivery_status(message_id, to_email, subject)

        except SendFailedError as e:
            error_str = str(e).lower()
            definitive_failure_keywords = [
                "invalid email address", 
                "recipient email address is not valid",
                "invalid sender",
                "event: hard_bounce",
                "event: invalid_email",
                "event: error"
            ]
            if any(keyword in error_str for keyword in definitive_failure_keywords):
                return False
            
            raise
        except ApiException as e: # Catch-all for other APIExceptions
            raise SendFailedError(f"Unexpected Brevo API error for '{subject}' to {to_email}: {e}")

    def _get_transactional_emails_api(self) -> sib_api_v3_sdk.TransactionalEmailsApi:
        """Helper to get an instance of the TransactionalEmailsApi."""
        return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))

    async def _execute_send_email_request(self, to_email: str, subject: str, html_content: str,
                                          metadata: Optional[Dict[str, Any]]) -> str:
        """
        Sends the email request to Brevo and returns the message ID.
        Runs the blocking API call in an executor.
        """
        api_instance = self._get_transactional_emails_api()
        
        sender_obj = sib_api_v3_sdk.SendSmtpEmailSender(name=self.sender_name, email=self.sender_email)
        to_obj = [sib_api_v3_sdk.SendSmtpEmailTo(email=to_email)]

        send_smtp_email_details = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender_obj,
            to=to_obj,
            html_content=html_content,
            subject=subject
        )
        if metadata:
            send_smtp_email_details.params = metadata

        try:
            loop = asyncio.get_event_loop()
            api_response = await loop.run_in_executor(
                None,  # Default ThreadPoolExecutor
                api_instance.send_transac_email,
                send_smtp_email_details
            )
            if hasattr(api_response, 'message_id') and api_response.message_id:
                return api_response.message_id
            else:
                # This case indicates a problem with Brevo's response format or an unexpected success response
                raise SendFailedError(f"Brevo API did not return a messageId for email to {to_email}, subject '{subject}'. Response: {api_response}")
        except ApiException as e:
            self._handle_initial_send_api_exception(e, to_email, subject) # This helper will raise SendFailedError

    def _handle_initial_send_api_exception(self, e: ApiException, to_email: str, subject: str):
        """
        Handles ApiException specifically for the initial send_transac_email call.
        Raises SendFailedError, which might be caught by `send` to return False for invalid emails.
        """
        error_body = e.body
        error_message_detail = str(e) # Fallback
        
        if isinstance(error_body, str):
            try:
                error_details_json = json.loads(error_body)
                error_message_detail = error_details_json.get("message", error_message_detail)
            except json.JSONDecodeError:
                # Keep the original exception string if body isn't valid JSON
                pass
        
        # Keywords indicating the email could not be sent due to fundamental invalidity
        # These map to returning False in the main `send` method.
        # Brevo error codes like 'invalid_parameter' often come with descriptive messages.
        invalidity_keywords = [
            "invalid email address",
            "recipient email address is not valid",
            "sender email is not valid",
            "invalid sender"
        ]
        if any(keyword in error_message_detail.lower() for keyword in invalidity_keywords):
            raise SendFailedError(f"Invalid email address or sender for '{subject}' to {to_email}: {error_message_detail}")
        else:
            # For other API errors during initial send (e.g. auth, quota)
            raise SendFailedError(f"Brevo API exception when trying to send '{subject}' to {to_email}: {error_message_detail}")


    async def _poll_for_delivery_status(self, message_id: str, to_email: str, subject: str) -> bool:
        """
        Polls Brevo for the delivery status of the sent email.
        Returns True if delivered, raises SendFailedError for hard bounces/errors,
        or returns False on timeout if status is undetermined.
        """
        api_instance = self._get_transactional_emails_api()
        max_attempts = self.max_poll_attempts  # Use instance attribute
        poll_interval_base = self.poll_interval_base  # Use instance attribute

        for attempt in range(max_attempts):
            try:
                loop = asyncio.get_event_loop()
                
                # Prepare the call with functools.partial
                call_with_args = functools.partial(
                    api_instance.get_email_event_report,
                    message_id=message_id,
                    email=to_email,
                    # It's good practice to limit the scope, e.g., by date or specific events if possible
                    # For now, keeping it simple as per previous logic, but this is an area for refinement.
                    # Adding a limit as it's generally a good practice for API calls returning lists.
                    limit=10 
                )
                
                events_response = await loop.run_in_executor(
                    None,
                    call_with_args
                )

                if events_response and hasattr(events_response, 'events') and events_response.events:
                    for event_obj in events_response.events:
                        event_name = event_obj.event.lower()
                        if event_name == 'delivered':
                            return True
                        # Terminal failure events
                        elif event_name in ['hard_bounce', 'invalid_email', 'error']: 
                            reason = getattr(event_obj, 'reason', 'N/A')
                            # Raise SendFailedError so `send` can catch it and return False
                            raise SendFailedError(f"Email to {to_email} subject '{subject}' resulted in event: {event_name}. Reason: {reason}")
                        # Other events (e.g., 'sent', 'soft_bounce', 'opened', 'clicked') are not final for this check
                
                # If no definitive event, wait and retry
                if attempt < max_attempts - 1:
                    # Exponential backoff for retries
                    await asyncio.sleep(poll_interval_base * (attempt + 1))  
                else:
                    # Max attempts reached without definitive 'delivered' or hard failure event
                    return False 

            except ApiException as e:
                # This exception is from get_email_event_report call itself (e.g., auth error, rate limit)
                # It means we cannot determine the status.
                raise SendFailedError(f"Could not verify email status for {message_id} due to API polling error: {e}")
        
        # Fallback, though max_attempts logic should handle it.
        return False
