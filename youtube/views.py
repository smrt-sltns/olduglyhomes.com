from django.shortcuts import render
from .authorize import google_auth, google_auth_callback
from .models import YoutubeCreds, Channel, Video, Comment, CommentReply
from django.contrib.auth.models import User 
from django.http import HttpResponse


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



def add_channel(request):
    if request.method == "POST":
        api_key = request.POST['api_key']
        channel_id = request.POST['channel_id']
        channel_name = request.POST['channel_name'] 
        print(api_key, channel_id, channel_name)
        user = request.user
        if not YoutubeCreds.objects.filter(api_key=api_key).exists():
            
            creds = YoutubeCreds(api_key=api_key, user=user)
            channel_username = str(channel_name).split(" ")
            username = "_".join(channel_username)
            channel = Channel(
                user=user, creds = creds, 
                name = channel_name, 
                channel_username=username,
                channel_id=channel_id
            )
            print("creds and channel have been created!")
            return HttpResponse("New channel added!")
    else: 
        return render(request, "youtube/add_channel.html")