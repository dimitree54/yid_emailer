from abc import ABC, abstractmethod
from typing import Dict, Any


class EmailTemplateBase(ABC):
    @abstractmethod
    def get_subject(self) -> str:
        """
        Get the email subject.

        Returns:
            Email subject string
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata for the email.

        Returns:
            Dictionary of email metadata
        """
        pass

    @abstractmethod
    def render(self) -> str:
        """
        Render the email template.

        Returns:
            Rendered HTML content
        """
        pass

    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to a maximum length, adding an ellipsis if truncated.

        Args:
            text: The text to truncate.
            max_length: The maximum length of the text.

        Returns:
            The truncated text.
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
