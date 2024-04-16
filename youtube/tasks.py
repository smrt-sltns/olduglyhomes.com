from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Video
from django.core.serializers.json import DjangoJSONEncoder
import json
from .save_data import save_videos



@shared_task()
def task_save_video():
    """
    This will run once every day. 
    
    1. Get info of Channel and Videos from 
       Youtube Data API and save to db. 
    2. Send email notifying if there are 
        changes in the subscriber count.
    """
    save_videos()
   