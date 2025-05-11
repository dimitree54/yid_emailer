import os
import unittest

from emailer.providers.brevo_provider import BrevoEmailProvider
from path2dream.templates.error_report_template import ErrorReportTemplate


class TestBrevoEmail(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        api_key = os.environ.get('BREVO_API_KEY')
        self.sender_name = "GitHub Tests"
        self.sender_email = "dimitree54@gmail.com"
        self.assertIsNotNone(api_key, "BREVO_API_KEY not found in environment variables")
        self.emailer = BrevoEmailProvider(brevo_api_key=api_key, sender_email=self.sender_email, sender_name=self.sender_name)


    async def test_send_email(self):
        recipient_email = "dimitree54@gmail.com"
        template = ErrorReportTemplate(
            error="It is test email from GitHub Actions of the repo yid_emailer",
            company_name="YiD", sender_name=self.sender_name, sender_email=self.sender_email
        )
        success = await self.emailer.send(recipient_email, template.get_subject(), template.render(), template.get_metadata())
        self.assertTrue(success)


    async def test_fail_send(self):
        recipient_email = "dimitree54@gmail.com"
        template = ErrorReportTemplate(
            error="It is test email from GitHub Actions of the repo yid_emailer",
            company_name="YiD", sender_name=self.sender_name, sender_email=self.sender_email
        )
        self.emailer.sender_email = "email_that_i_do_not_own@gmail.com"
        success = await self.emailer.send(recipient_email, template.get_subject(), template.render(), template.get_metadata())
        self.assertFalse(success)
