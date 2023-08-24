from celery import shared_task
from django.conf import settings 
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection, send_mail, send_mass_mail



@shared_task
def send_mail_token(title, message, email_template, user_email:list, user):
    msg_html = render_to_string(email_template, {'user':user})
    send_mail(
        title,
        message,
        settings.EMAIL_HOST_USER,
        [user_email,],
        html_message=msg_html,
        )
    # except Exception as e:
    #     print(e)
    #     pass 