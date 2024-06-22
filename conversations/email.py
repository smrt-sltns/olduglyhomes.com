from django.core.mail import send_mail
from django.conf import settings

def send_conversation_email(json_data):
    subject = f"Web hook test email "
    message = f"{json_data}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['kundanpandey.dev@gmail.com']

    send_mail(subject, message, from_email, recipient_list)
