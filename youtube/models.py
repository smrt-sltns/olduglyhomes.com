from django.db import models
from django.contrib.auth.models import User



class YoutubeCreds(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    api_key = models.CharField(max_length=150,unique=True, null=False, blank=False, help_text="Please prove a valid api key.")
    client_id = models.CharField(max_length=150,unique=True, null=True, blank=True)
    client_secret = models.CharField(max_length=150,unique=True, null=True, blank=True)
    access_token = models.CharField(max_length=300,unique=True, null=True, blank=True)
    refresh_token = models.CharField(max_length=300,unique=True, null=True, blank=True)
    unique_name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    class Meta:
        verbose_name = "Creds"
        verbose_name_plural = "Creds"

    def __str__(self):
        return f"{self.unique_name} | {self.user.email}"
    
    

class Channel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    creds = models.ForeignKey(YoutubeCreds, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    channel_id = models.CharField(max_length=100,unique=True, null=False, blank=False)
    channel_username = models.CharField(max_length=100, null=True, blank=True)  
    subscribers = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Channel"
        verbose_name_plural = "Channels"
        
    def __str__(self):
        return self.channel_username
    



class Video(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=False, blank=False)
    video_id = models.CharField(max_length=100, unique=True, null=False, blank=False)
    video_title = models.CharField(max_length=500, null=True, blank=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0) 
    published_at = models.CharField(max_length=100, null=True, blank=True) #youtube data 
    published_datetime = models.DateTimeField(null=True, blank=True)
    store_at = models.DateTimeField(auto_now=True) #datetime when the video was capture by us 
    
    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        
    def __str__(self):
        return f"{self.channel.channel_username} | {self.video_title}"
    

    
class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=False, blank=False)
    comment = models.CharField(max_length=500, null=True, blank=True)
    comment_id = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100, null=False, blank=False)
    
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        
    def __str__(self):
        return f"{self.comment} | {self.video.video_title}"
    

    
class CommentReply(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=False, blank=False)
    comment = models.CharField(max_length=500, null=True, blank=True)
    comment_id = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100, null=False, blank=False)
    
    class Meta:
        verbose_name = "Comment Reply"
        verbose_name_plural = "Comment Replies"
        
    def __str__(self):
        return f"{self.comment} | {self.video.video_title}"
    