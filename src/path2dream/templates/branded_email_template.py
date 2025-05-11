from abc import abstractmethod

from emailer.templates.email_template import EmailTemplateBase


class BrandedEmailTemplate(EmailTemplateBase):
    def __init__(self, company_name: str, sender_name: str, sender_email: str):
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.company_name = company_name

    def _get_common_styles(self) -> str:
        """
        Returns common CSS styles for branded emails.
        """
        return """
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                background-color: #f4f4f4;
            }
            .container {
                padding: 20px;
                background-color: #ffffff;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .header {
                background-color: #1a2c40; /* Dark blue, adjust as needed */
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
            }
            .content {
                padding: 20px;
            }
            .footer {
                text-align: center;
                padding: 20px;
                font-size: 12px;
                color: #666;
            }
            .button {
                display: inline-block;
                background-color: #3498db; /* Primary button color */
                color: white !important; /* Ensure text is white */
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 15px;
            }
            a.button {
                color: white !important;
            }
        """

    @abstractmethod
    def _get_email_content_html(self) -> str:
        """
        Get the specific HTML content for the email body.
        This should be implemented by subclasses.

        Returns:
            HTML string for the email's main content.
        """
        pass

    def render(self) -> str:
        """
        Render the full HTML email using a common structure.

        Returns:
            Rendered HTML content.
        """
        subject = self.get_subject()
        email_content_html = self._get_email_content_html()
        common_styles = self._get_common_styles()

        html = f"""
        <!DOCTYPE html>
        <html lang=\"en\">
        <head>
            <meta charset=\"UTF-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
            <title>{subject}</title>
            <style>
                {common_styles}
            </style>
        </head>
        <body>
            <div class=\"container\">
                <div class=\"header\">
                    <h1>{self.company_name}</h1>
                </div>
                <div class=\"content\">
                    {email_content_html}
                </div>
                <div class=\"footer\">
                    <p>Sender: {self.sender_name} &lt;{self.sender_email}&gt;</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html 