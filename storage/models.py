from django.db import models
from facebook.models import AccountPages

# Create your models here.


class Campaign(models.Model):
    
    page = models.ForeignKey(AccountPages, on_delete=models.CASCADE, null=True, blank=True)
    campaign_id = models.CharField(max_length=100)
    campaign_name = models.CharField(max_length=150)
    effective_status = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.campaign_name} | {self.campaign_id} "
    

class Adset(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    page = models.ForeignKey(AccountPages, on_delete=models.PROTECT, null=True, blank=True)
    adset_id = models.CharField(max_length=100, null=False, blank=False)
    adset_name = models.CharField(max_length=150, null=True, blank=True)
    
    def __str__(self):
        return f"{self.adset_name} | {self.adset_id}"
    
    
    
class Ad(models.Model):
    adset = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    page = models.ForeignKey(AccountPages, on_delete=models.PROTECT, null=True, blank=True)
    ad_id = models.CharField(max_length=100, null=False, blank=False)
    ad_name = models.CharField(max_length=150, null=True, blank=True)
    effective_object_story_id = models.CharField(max_length=200)
    effective_status = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.ad_name} | {self.ad_id}"
    
    
class Comment(models.Model):
    ad = models.CharField(Ad, on_delete=models.PROTECT, null=True, blank=True)
    comment_id = models.CharField(max_length=100, null=False, blank=False)
    comment_message = models.CharField(max_length=500, null=True, blank=True )
    
    #all comments will be positive if not marked negative 
    is_negative = models.BooleanField(default=False)
    is_ignored = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    
    facebook_create_time = models.CharField(max_length=100, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.comment_message} | {self.comment_id} | AD = {self.ad.ad_name}" 