from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from celery import Celery, shared_task
from facebook.models import Creds, AccountPages, AccountsAd
from facebook.utils import get_long_lived_access_token
from facebook.views import save_account_pages



def is_datefield_one_month_old(obj):
    current_date = timezone.now().date()
    if obj.has_ad_accounts:
        difference = current_date - obj.create_date
        # Calculate the number of days in a month (approximately)
        days_in_month = 30.44  # Average days in a month
        if difference >= timedelta(days=days_in_month):
            status = True
        else:
            status = False
    else: 
        status = False
    print(status)
    return status


def renew_access_token(user_id):
    user = User.objects.get(id=user_id)
    cred = Creds.objects.get(user=user)
    status = is_datefield_one_month_old(cred)
    if status:
        token = cred.LONGLIVED_ACCESS_TOKEN
        api_key = cred.APP_ID
        api_secret = cred.APP_SECRET
        long_lived_token = get_long_lived_access_token(api_key=api_key, api_secret=api_secret,access_token=token)
        cred.ACCESS_TOKEN = token 
        cred.LONGLIVED_ACCESS_TOKEN = long_lived_token # renew access token for creds models
        cred.create_date = timezone.now().date()
        cred.save()  
        print(f"Renewed Access token for {user.email}")
        save_account_pages(user=user) # renew access token for all the pages 

        adaccounts = AccountsAd.objects.filter(user=user)
        for ad in adaccounts:
            page_token = ad.page_associated.longlived_access_token
            ad_token = ad.access_token
            if page_token != ad_token:
                ad.access_token = page_token # changing access token of the ad account 
                ad.save()
                print(f"Access token of {ad.ad_account_name} is changed!" )
    








    

if __name__ == "__main__":
    cred = Creds.objects.get(id=6)
    is_datefield_one_month_old(cred)
# check if the long lived access token in a month old 
