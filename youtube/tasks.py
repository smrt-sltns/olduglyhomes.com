from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import YoutubeCreds
from django.core.serializers.json import DjangoJSONEncoder
import json
from .save_data import save_videos




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
        save_videos(unique_name)
    