from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from azure.communication.email import (
    EmailClient,
    EmailContent,
    EmailAddress,
    EmailMessage,
    EmailRecipients,
    EmailAttachment,
)


import time
import logging
from .logger import SimpleErrorHandler
from .utils import convert_attachment


class ACSEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        if not settings.ACS_CONNECTION_STRING:
            raise ValueError("ACS_CONNECTION_STRING is not set.")
        if not settings.ACS_SENDER_EMAIL:
            raise ValueError("ACS_SENDER_EMAIL is not set.")
        self.connection = EmailClient.from_connection_string(
            settings.ACS_CONNECTION_STRING
        )
        self.sender_email = settings.ACS_SENDER_EMAIL

        log_handler = SimpleErrorHandler()
        self.log = logging.getLogger("ACSEmailBackend")
        self.log.addHandler(log_handler)

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        sent = 0
        for message in email_messages:
            sent_status = self._send(message)
            if sent_status:
                sent += 1
        return sent

    def _send(self, message):
        if not message.recipients():
            return False
        to_emails = message.to
        cc_emails = message.cc
        bcc_emails = message.bcc
        subject = message.subject
        html_body = message.body if "<html>" in message.body else ""
        plain_body = message.body if "<html>" not in message.body else ""
        email_content = EmailContent(
            subject=subject, plain_text=plain_body, html=html_body
        )
        to_addresses = [EmailAddress(email=to_email) for to_email in to_emails]
        cc_addresses = [EmailAddress(email=cc_email) for cc_email in cc_emails]
        bcc_addresses = [EmailAddress(email=bcc_email) for bcc_email in bcc_emails]
        email_recipients = EmailRecipients(
            to=to_addresses, cc=cc_addresses, bcc=bcc_addresses
        )
        email_attachments = []
        for attachment in message.attachments:
            try:
                converter = convert_attachment(attachment)
                file_name, file_type = converter.get_filename().split(".")
                attachment = EmailAttachment(
                    name=file_name,
                    content=converter.get_file(),
                    content_type=file_type,
                )
            except Exception as e:
                print(e)
            else:
                email_attachments.append(attachment)
        email_message = EmailMessage(
            sender=self.sender_email,
            recipients=email_recipients,
            content=email_content,
            attachments=email_attachments,
        )
        response = self.connection.send(email_message)
        if (
            not response
            or response.message_id == "undefined"
            or response.message_id == ""
        ) and self.fail_silently:
            self.log.info("Message Id not found.")
        else:
            self.log.info("Send email succeeded for message_id :" + response.message_id)
            message_id = response.message_id
            counter = 0
            while True and not self.fail_silently:
                counter += 1
                send_status = self.connection.get_send_status(message_id)

                if send_status:
                    self.log.info(
                        f"Email status for message_id {message_id} is {send_status.status}."
                    )
                if send_status.status.lower() == "queued" and counter < 12:
                    time.sleep(10)  # wait for 10 seconds before checking next time.
                    counter += 1
                else:
                    if send_status.status.lower() == "outfordelivery":
                        self.log.info(f"Email delivered for message_id {message_id}.")
                        break
                    else:
                        self.log.error(
                            "Looks like we timed out for checking email send status."
                        )
                        break
        return True

    def close(self):
        pass
