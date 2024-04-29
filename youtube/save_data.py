from youtube.utils.channels import videos 
from youtube.utils.comments import comments 
from .models import YoutubeCreds, Channel, Video, Comment, CommentReply
from .email import email_subscriber_change
from datetime import datetime
from django.utils.timezone import make_aware

"""
Make all first api call to save data in database.
"""

def string_to_datetime(date_string):
    datetime_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
    aware_datetime = make_aware(datetime_obj)
    return aware_datetime



def save_videos(unique_name):
    """
    Get Channel info (subscriber count)
    and Video info (Likes, dislikes, comment count etc.)
    and save to db. 
    Send email if there are subscriber count changes.
    """ 
    cred = YoutubeCreds.objects.filter(unique_name=unique_name).first()
    channel = Channel.objects.filter(creds=cred).first()
    channel_data, videos_data = videos(api_key=cred.api_key, channel_id=channel.channel_id )
    email_subscriber_change(previous_subs_count=int(channel.subscribers), current_subs_count=int(channel_data[2]), channel_name=channel.name)
    if len(channel_data) != 0:
        channel.subscribers = channel_data[2]
        channel.save()
    for video in videos_data : 
        if not Video.objects.filter(channel=channel, video_id=video[0]).exists():
            Video.objects.create(
                channel = channel,
                video_id = video[0],
                video_title = video[1],
                views=int(video[2]),
                likes = int(video[3]), dislikes=int(video[4]),
                comments_count=int(video[5]), 
                published_at=video[6],
                published_datetime=string_to_datetime(video[6])
            )
        else: 
            vd = Video.objects.get(video_id=video[0])
            vd.video_title = video[1]
            vd.views=int(video[2])
            vd.likes = int(video[3])
            vd.dislikes=int(video[4])
            vd.comments_count=int(video[5]) 
            vd.published_at=video[6]
            vd.published_datetime=string_to_datetime(video[6])
            vd.save()


