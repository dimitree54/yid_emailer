from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class EmailProvider(ABC):
    """Interface for email providers."""
    def __init__(self, sender_name: str, sender_email: str):
        self.sender_email = sender_email
        self.sender_name = sender_name

    @abstractmethod
    async def send(self, to_email: str, subject: str, html_content: str,
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send an email using this provider.

        Args:
            to_email: The recipient's email address
            subject: The email subject
            html_content: The HTML content of the email
            metadata: Optional metadata for the email

        Returns:
            True if the email was sent successfully, False otherwise
        """
        pass
