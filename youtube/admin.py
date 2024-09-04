from django.contrib import admin
from .models import YoutubeCreds, Channel, Video, Comment,  CommentReply, EmailRecord

admin.site.register(YoutubeCreds)
admin.site.register(Channel)
admin.site.register(Video)
admin.site.register(Comment)
admin.site.register(CommentReply)
admin.site.register(EmailRecord)



# Register your models here.
