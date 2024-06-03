from django.shortcuts import render, redirect
from .authorize import google_auth, google_auth_callback
from .models import YoutubeCreds, Channel, Video, Comment, CommentReply
from django.contrib.auth.models import User 
from django.http import HttpResponse
from django.contrib import messages
from facebook.decorator import custom_login_required, youtube_login_decorator
from facebook.models import DefaultApp

@youtube_login_decorator
def YoutubeIndex(request):
    """Display Channel and Video info in a HTML table."""
    channel_id = request.GET.get("channel_id", None)
    if not channel_id: 
        chnl = Channel.objects.filter(user=request.user)
        if not chnl.exists():
            messages.info(request, "Please add your Youtube channels to continue.")
            return render(request, "youtube/index.html")
        else:
            channel_id = chnl.first().channel_id
    channel = Channel.objects.get(channel_id=channel_id)
    sort_by = request.GET.get('sort_by', '')
    
    videos = Video.objects.filter(channel=channel).all()
    if sort_by == "published_at":
        videos = Video.objects.filter(channel=channel).order_by("published_datetime").all()
    elif sort_by == "" or sort_by == None:
        videos = Video.objects.filter(channel=channel).order_by("-published_datetime").all()
    else:
        videos = Video.objects.filter(channel=channel).order_by(f"-{sort_by}")

    context = {
        "channel": channel,
        "videos": videos, 
        "channels" : Channel.objects.all(),
    }
    return render(request, "youtube/index.html", context)


@youtube_login_decorator
def add_channel(request):
    if request.method == "POST":
        api_key = request.POST['api_key']
        channel_id = request.POST['channel_id']
        channel_name = request.POST['channel_name'] 
        print(api_key, channel_id, channel_name)
        user = request.user
        if YoutubeCreds.objects.filter(api_key=api_key).exists():
            messages.info(request, "Channel with this api key already exists!")
            return render(request, "youtube/add_channel.html")
        if Channel.objects.filter(channel_id=channel_id).exists():
            messages.info(request, "Channel with this ID already exists!")
            return render(request, "youtube/add_channel.html")
        
        creds = YoutubeCreds(api_key=api_key, user=user)
        creds.save()
        channel_username = str(channel_name).split(" ")
        username = "_".join(channel_username)
        channel = Channel(
            user=user, creds = creds, 
            name = channel_name, 
            channel_username=username,
            channel_id=channel_id
        )
        channel.save()
        messages.success(request, "New channel added!")
        # return HttpResponse("New channel added!")
    
        return redirect("youtube-index")
    else: 
        return render(request, "youtube/add_channel.html")
    
    
    
def switch_youtube(request):
    """Switch from yoututbe to facebook."""
    
    # if not DefaultApp.objects.filter(user=request.user).exists():
    #     default_app = DefaultApp()
    #     default_app.user = request.user
    #     default_app.save()
    # default_app = DefaultApp.objects.filter(user=request.user).first()
    # if default_app.to_youtube == True:
    #     default_app.to_youtube = False
    # else: 
    #     default_app.to_youtube = True
    # print(default_app.to_youtube)
    # default_app.save()
    return redirect("youtube-index")

def switch_facebook(request):
    return redirect('home')
