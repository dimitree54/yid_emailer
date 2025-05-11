from emailer.providers.email_provider import EmailProvider
from emailer.templates.email_template import EmailTemplateBase
from path2dream.templates.error_report_template import ErrorReportTemplate
from path2dream.templates.purchase_confirmation_template import PurchaseConfirmationEmailTemplate
from path2dream.templates.results_template import ResultsEmailTemplate


class EmailService:
    """Service for sending emails using various providers."""
    
    def __init__(self, provider: EmailProvider, developer_email: str, company_name: str, sender_name: str, sender_email: str):
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.company_name = company_name
        self.provider = provider
        self.developer_email = developer_email

    async def send_email(self, template: EmailTemplateBase, to_email: str) -> bool:
        subject = template.get_subject()
        html_content = template.render()
        metadata = template.get_metadata()

        success = await self.provider.send(to_email, subject, html_content, metadata)
        return success
    
    async def send_confirmation_email(self, purchase_info: str, recipient_email: str) -> bool:
        template = PurchaseConfirmationEmailTemplate(
            purchase_info=purchase_info,
            sender_email=self.sender_email, sender_name=self.sender_name, company_name=self.company_name)
        return await self.send_email(template, recipient_email)
    
    async def send_results_email(self, result_doc_link: str, recipient_email: str) -> bool:
        template = ResultsEmailTemplate(
            result_doc_link=result_doc_link,
            company_name=self.company_name, sender_email=self.sender_email, sender_name=self.sender_name)
        return await self.send_email(template, recipient_email)
    
    async def send_developer_notification(self, error: str, company_name: str, sender_name: str, sender_email: str) -> bool:
        template = ErrorReportTemplate(error, company_name, sender_name, sender_email)
        return await self.send_email(template, self.developer_email)
