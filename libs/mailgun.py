from requests import Response, post
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class MailgunException(Exception):
    def __init__(self, message: str):
        self.message = message


class Mailgun:
    MAILGUN_KEY = os.environ.get('MAILGUN_KEY', None)
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', None)

    FROM_TITLE = 'Pricing service'
    FROM_EMAIL = f'do-not-reply@{MAILGUN_DOMAIN}'
    MAILGUN_URL = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_KEY is None:
            raise MailgunException("Failed to load Mailgun API KEY")
        if cls.MAILGUN_DOMAIN is None:
            raise MailgunException("Failed to load Mailgun DOMAIN_NAME")

        response = post(
            cls.MAILGUN_URL,
            auth=("api", cls.MAILGUN_KEY),
            data={"from": f"{cls.FROM_TITLE} {cls.FROM_EMAIL}",
                  "to": [email],
                  "subject": subject,
                  "text": text,
                  "html": html,
                  })

        if response.status_code != 200:
            print(response, response.status_code)
            raise MailgunException("An error occurred while sending emails")

        return response

#
# if __name__ == '__main__':
#     print(os.environ['MAILGUN_KEY'])
#     print(os.environ['MAILGUN_DOMAIN'])
#     Mailgun.send_email(['lolo.edinburgh@gmail.com'],
#                        "Hello",
#                        "This is a test",
#                        '<h4>This is a test</h4>'
#                        )
