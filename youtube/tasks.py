from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import YoutubeCreds, EmailRecord
from django.core.mail import EmailMessage
from django.core.serializers.json import DjangoJSONEncoder
import json
from .save_data import save_videos
from django.utils import timezone



def email_failed_automation(error):
    """send email to self if the automation is failed with the reason"""
    """seld email once a day."""
    if not has_today_record():
        email_record = EmailRecord.objects.create(reason=error, email='kundanpandey.dev@gmail.com')
        email = EmailMessage(
        subject='Failed Subscription Automation',
        body=error,
        from_email='coboaccess2@gmail.com',
        to=['kundanpandey.dev@gmail.com'],
        )
        # email.content_subtype = 'html'
        email.send()



def has_today_record():
    # Get the current date
    today = timezone.now().date()

    # Check if there is any record created today
    record_exists = EmailRecord.objects.filter(
        created_at__date=today
    ).exists()

    return record_exists

@shared_task()
def task_save_video():
    """
    Takes in unique names of the existing channel in db 
    and then call the GET API to get the channel data. 
    All the data (subscriber, videos (id, likes, comment count etc.))
    is saved / updated in the db. 
    If there are changes in the subscribers count then a mail is 
    sent out. 
    """
    channels = YoutubeCreds.objects.all()
    for channel in channels:
        unique_name = channel.unique_name
        try:
            
            save_videos(unique_name)
        except Exception as e:
            email_failed_automation(error=str(e))
    