from django.db import models
from facebook.models import AccountPages


class Conversation(models.Model):
    page = models.ForeignKey(AccountPages, on_delete=models.CASCADE, related_name='conversations')
    conversation_id = models.CharField(max_length=255)
    sender_id = models.CharField(max_length=255)
    message = models.TextField()
    created_time = models.DateTimeField()

    def __str__(self):
        return f'Conversation {self.conversation_id} on {self.page.name}'

# Create your models here.
