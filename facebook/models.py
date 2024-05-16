from django.db import models
from django.contrib.auth.models import User 
# from .utils import get_long_lived_access_token



# store api credentials and access token with all ther permissions
class Creds(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    APP_ID = models.CharField(max_length=100, null=True, blank=True, unique=True)
    APP_SECRET = models.CharField(max_length=200, null=True, blank=True, unique=True)
    ACCESS_TOKEN = models.CharField(max_length=400, null=True, blank=True, unique=True)
    LONGLIVED_ACCESS_TOKEN = models.CharField(max_length=400, null=True, blank=True, unique=True)
    create_date = models.DateField(auto_now_add=True, null=True, blank=True)

    # check if app key, app secret and access token are sync properly 
    has_app_key = models.BooleanField(default=False)
    has_access_token = models.BooleanField(default=False)
    has_ad_accounts = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Credentials"

    def __str__(self):
        return self.user.username 
    
    def save(self, *args, **kwargs):
        super(Creds, self).save(*args, **kwargs)



# store all the Facebook pages credentials and access token with permissions 
class AccountPages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    page_id = models.CharField(max_length=100, null=True, blank=True,)
    page_name = models.CharField(max_length=50, null=True, blank=True)
    page_access_token = models.CharField(max_length=400, null=True, blank=True)
    longlived_access_token = models.CharField(max_length=400, null=True, blank=True)
    has_access_token = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Account Pages"

    def __str__(self):
        return self.page_name 


# store all the ad accounts and pages running the ad accounts
class AccountsAd(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    page_associated = models.ForeignKey(AccountPages, on_delete=models.CASCADE, null=True, blank=True)
    ad_account_id = models.CharField(max_length=30, null=True, blank=True, unique=True)
    ad_account_name = models.CharField(max_length=200, null=True, blank=True)
    access_token = models.CharField(max_length=2000, null=True, blank=True)
    class Meta:
        verbose_name_plural = "Account Ads"

    def __str__(self):
        return self.ad_account_name



class ContactUs(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    phone = models.CharField(max_length=100, null=True, blank=True)
    message = models.CharField(max_length=600, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True )
    
    def __str__(self):
        return f"{self.user.email} | {self.created_at}"
    

class CommentActionsErrors(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    comment_message = models.CharField(max_length=200, null=True, blank=True)
    comment_id = models.CharField(max_length=100, null=False, blank=False)
    action = models.CharField(max_length=100, null=False, blank=False) # possible values are hide / unhide 
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email} | {self.created_at}"


class IgnoredComments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #comment info
    comment = models.CharField(max_length=250, null=True, blank=True)
    comment_id = models.CharField(max_length=100)
    created_date = models.CharField(max_length=100)
    #ad info
    ad_name = models.CharField(max_length=100),
    ad_id = models.CharField(max_length=100)
     
    def __str__(self):
        return "{}, {}".format(self.user.usename, self.comment)



class DefaultApp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    to_youtube = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user} | Youtube {self.to_youtube}"

    

