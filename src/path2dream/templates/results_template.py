from typing import Dict, Any

from .branded_email_template import BrandedEmailTemplate


class ResultsEmailTemplate(BrandedEmailTemplate):
    def __init__(self, result_doc_link: str, company_name: str, sender_name: str, sender_email: str):
        super().__init__(company_name, sender_name, sender_email)
        self.result_doc_link = result_doc_link

    def get_subject(self) -> str:
        return f"Your {self.company_name} Idea Analysis Results"
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "results",
            "result_doc_link": self.result_doc_link
        }
    
    def _get_email_content_html(self) -> str:
        doc_link = self.result_doc_link

        doc_link_button_html = ""
        if doc_link:
            doc_link_button_html = f"""
            <div style="margin: 20px 0; text-align: center;">
                <a href="{doc_link}" target="_blank" class="button">View Full Report</a>
            </div>
            """
        
        content_html = f"""
            <h2>Your Idea Analysis is Ready!</h2>
            <p>Hello,</p>
            <p>We've completed the analysis of your idea. Here are the results:</p>

            {doc_link_button_html}

            <p>Thank you for using {self.company_name}!</p>
            <p>If you have any questions about your results, feel free to <a href="mailto:{self.sender_email}">contact us</a>.</p>
        """
        return content_html
