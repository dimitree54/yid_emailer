from typing import Dict, Any

from path2dream.templates.branded_email_template import BrandedEmailTemplate


class EmailConfirmationTemplate(BrandedEmailTemplate):
    def __init__(self, confirmation_code: str, company_name: str, sender_name: str, sender_email: str):
        super().__init__(company_name, sender_name, sender_email)
        self.confirmation_code = confirmation_code

    def get_subject(self) -> str:
        return f"Confirm Your Email for {self.company_name}"

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "email_confirmation",
        }

    def _get_email_content_html(self) -> str:
        content_html = f"""
            <h2>Confirm Your Email Address</h2>
            <p>Hello,</p>
            <p>Thank you for signing up with {self.company_name}. Please use the confirmation code below to verify your email address.</p>

            <div style="background-color: #f0f4f8; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0; text-align: center;">
                <p style="font-size: 24px; font-weight: bold; margin: 0;">{self.confirmation_code}</p>
            </div>

            <p>If you did not request this email, please ignore it.</p>
            <p>If you have any questions, please don\'t hesitate to <a href="mailto:{self.sender_email}?subject=Question%20about%20email%20confirmation">contact us</a>.</p>
        """
        return content_html 