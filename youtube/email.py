from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

RECIPIENT_LIST = ["kundanpandey.dev@gmail.com", ]

def email_subscriber_change(previous_subs_count:int, current_subs_count:int):
    """Send email if the are changes in the subscribers count."""
    
    if previous_subs_count != current_subs_count:
        if previous_subs_count < current_subs_count: 
            message_body = f"""<strong>You have <span style='color: green;'>gained</span> subscribers!</strong><br>
            Previous subscribers: {previous_subs_count}<br>
            Current subscribers: {current_subs_count}"""
        elif previous_subs_count > current_subs_count: 
            message_body = f"""<strong>You have <span style="color: red;">lost</span> subscribers!</strong><br>
            Previous subscribers: {previous_subs_count}<br>
            Current subscribers: {current_subs_count}"""
        email = EmailMessage(
        subject='Subscription Notification',
        body=message_body,
        from_email='coboaccess2@gmail.com',
        to=RECIPIENT_LIST,
        )
        email.content_subtype = 'html'
        email.send()