from django.shortcuts import render
from .authorize import google_auth, google_auth_callback
from .models import YoutubeCreds, Channel, Video, Comment, CommentReply



def index(request):
    """Display Channel and Video info in a HTML table."""
    channel_id = request.GET.get("channel_id", None)
    print(channel_id)
    if not channel_id: 
        channel_id = Channel.objects.first().channel_id
    channel = Channel.objects.get(channel_id=channel_id)
    sort_by = request.GET.get('sort_by', '')
    
    videos = Video.objects.filter(channel=channel).all()
    len(videos)
    if sort_by == "published_at":
        videos = Video.objects.filter(channel=channel).order_by("-pk").all()[::-1]
    elif sort_by == "" or sort_by == None:
        videos = Video.objects.filter(channel=channel).all()
    else:
        videos = Video.objects.filter(channel=channel).order_by(f"-{sort_by}")
    
    context = {
        "channel": channel,
        "videos": videos, 
        "channels" : Channel.objects.all(),
    }
    return render(request, "youtube/index.html", context)
