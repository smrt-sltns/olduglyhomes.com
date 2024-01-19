from django.db import models
from django.contrib.auth.models import User 

# Create your models here.


class AdRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    account_id = models.CharField(max_length=200, null=True, blank=True)
    
    effective_object_story_id = models.CharField(max_length=200, blank=True,unique=False, null=True)
    campaign_name = models.CharField(max_length=200, null=True, blank=True)
    campaign_id = models.CharField(max_length=200, null=True, blank=True)
    campaign_spend = models.FloatField(default=0)
    campaign_spend_limit = models.FloatField(default=0.0)#limit set and if exceeded then expire the ad
    is_campaign_limit_set = models.BooleanField(default=False)
    
    
    adset_name = models.CharField(max_length=200, null=True, blank=True)
    adset_id = models.CharField(max_length=200, null=True, blank=True)
    adset_spend = models.FloatField(default=0)
    adset_spend_limit = models.FloatField(default=0.0)#limit set and if exceeded then expire the ad
    
    
    ad_name = models.CharField(max_length=200, null=True, blank=True)
    ad_id = models.CharField(max_length=200, null=True,unique=True, blank=True)
    
    ad_spend = models.FloatField(default=0.0)#current spend from facebook 
    ad_spend_limit = models.FloatField(default=0.0)#limit set and if exceeded then expire the ad
    
    mail_sent = models.BooleanField(default=False)#if mail is sent then expire the ad 
    
    expired = models.BooleanField(default=False)#id new limit is set then set to True 
    is_active = models.BooleanField(default=True) #track ads only if activate 
    is_limit_set = models.BooleanField(default=False) #track if limit is set
    created_datetime = models.DateTimeField(auto_now_add=True)    
    
    def __str__(self):
        title = f"{self.campaign_name} | {self.adset_name} | {self.ad_name}"
        return title 
    


class CampaignRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    campaign_name = models.CharField(max_length=100, null=True, blank=True)
    campaing_id = models.CharField(max_length=100, null=True, blank=True)
    campaign_spend = models.FloatField(default=0)
    last_edited = models.DateTimeField()
    created_datetime = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.campaign_name}"

    # def save(self):
    #     return super(CampaignRecord, self).save()



class AdSetRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    campaign = models.ForeignKey(CampaignRecord, on_delete=models.CASCADE, null=True, blank=True)
    adset_name = models.CharField(max_length=100, null=True, blank=True)
    adset_id = models.CharField(max_length=100, null=True, blank=True)
    adset_spend = models.FloatField(default=0)

    def __str__(self):
        return f"{self.campaign} | {self.adset_name}"
