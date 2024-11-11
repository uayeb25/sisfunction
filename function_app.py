import azure.functions as func
import logging
from dotenv import load_dotenv
import os
import requests


from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

app = func.FunctionApp()


@app.queue_trigger(
        arg_name="azqueue"
        , queue_name="activate"
        , connection="QueueAzureWebSobStorage"
)
def QueueTriggerFunctionActivateAccount(azqueue: func.QueueMessage):
        body = azqueue.get_body().decode('utf-8')

        sender = os.getenv('EMAIL_SENDER')
        api = os.getenv('API_DOMAIN')
        password = os.getenv('SG_KEY')

        SECRET_KEY_FUNC = os.getenv('SECRET_KEY_FUNC')

        response = requests.post(
                f"{api}/user/{body}/code",
                headers={"Authorization": SECRET_KEY_FUNC}
        )

        response.raise_for_status()
        code = response.json().get('code')

        message = Mail(
                from_email=sender,
                to_emails=body,
                subject='Expertos: Codigo de activación de cuenta',
                plain_text_content=f"Tu codigo de activación { code }",
                html_content=f"<strong>Tu codigo de activación: { code } </strong>"
        )

        try:
                sg = SendGridAPIClient(password)
                response = sg.send(message)
                logging.info(response.status_code)

        except Exception as e:
                print(str(e))
                if hasattr(e, 'body'):
                        print(e.body)

        logging.info('Python Queue trigger processed a message: %s', body )
