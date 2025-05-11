from typing import Dict, Any

from path2dream.templates.branded_email_template import BrandedEmailTemplate


class ErrorReportTemplate(BrandedEmailTemplate):
    def __init__(self, error: str, company_name: str, sender_name: str, sender_email: str):
        super().__init__(company_name, sender_name, sender_email)
        self.error = error

    def get_subject(self) -> str:
        return f"[ERROR] {self.company_name} Processing Error"
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "error_notification",
        }

    def _get_email_content_html(self) -> str:
        formatted_error = self.error.replace("\n", "<br>")

        html = f"""
                <h2>Error info:</h2>
                <div class=\"section\">
                    <div class=\"code\"><pre>{formatted_error}</pre></div>
                </div>
        """
        return html
