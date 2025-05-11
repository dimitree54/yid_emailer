from typing import Dict, Any

from path2dream.templates.branded_email_template import BrandedEmailTemplate


class PurchaseConfirmationEmailTemplate(BrandedEmailTemplate):
    def __init__(self, purchase_info: str,
                 company_name: str, sender_name: str, sender_email: str):
        super().__init__(company_name, sender_name, sender_email)
        self.purchase_info = purchase_info

    def get_subject(self) -> str:
        return f"Your {self.company_name} Idea Submission Confirmation"
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "confirmation",
        }

    def _get_email_content_html(self) -> str:
        content_html = f"""
            <h2>Thank You for Your Submission!</h2>
            <p>Hello,</p>
            <p>We've received your idea submission and your payment has been confirmed.</p>

            <h3>Purchase information:</h3>
            <div style=\"background-color: #f0f4f8; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0;\">
                <p>{self.purchase_info}</p>
            </div>

            <h3>What's Next?</h3>
            <p>We'll start processing your idea and you'll receive the results via emai. Usually it is done within 30 minutes, but may take up to 24 hours.</p>
            <p>If you have any questions in the meantime, please don't hesitate to contact us.</p>
            <a href=\"mailto:{self.sender_email}?subject=Question%20about%20my%20idea\" class=\"button\">Contact Us</a>
        """
        return content_html
