"""
Brevo Email Provider

This module implements the Brevo email provider.
"""

from typing import Dict, Any, Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from emailer.exceptions import SendFailedError
from emailer.providers.email_provider import EmailProvider


class BrevoEmailProvider(EmailProvider):
    """Email provider for Brevo (formerly Sendinblue)."""
    
    def __init__(self, brevo_api_key: str, sender_name: str, sender_email: str):
        """Initialize the Brevo email provider."""
        super().__init__(sender_name, sender_email)
        self.api_key = brevo_api_key
        
        # Set up Brevo client configuration
        self.configuration = sib_api_v3_sdk.Configuration()
        if self.api_key:
            self.configuration.api_key['api-key'] = self.api_key

    def send(self, to_email: str, subject: str, html_content: str, 
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            # Initialize API client
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))

            # Create sender
            sender = {"name": self.sender_name, "email": self.sender_email}

            # Create recipient
            to = [{"email": to_email}]

            # Create email object
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                html_content=html_content,
                sender=sender,
                subject=subject
            )

            # Send the email
            api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            raise SendFailedError(
                f"Brevo API exception when trying to send '{subject}' to {to_email}: {e}"
            )
