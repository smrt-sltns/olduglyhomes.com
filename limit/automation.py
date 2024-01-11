import requests 
from .models import AdRecord
from .utils import save_ads, email_to_file_name
from decouple import config 
from facebook.models import Creds
from django.contrib.auth.models import User 
from django.conf import settings 
import json 
import os 
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection, send_mail
from datetime import datetime, timedelta





def check_spend_limit(user_id="3"):
    """
    run every 20 minutes on selected ads 
    which have their limit set and if limit 
    set has exceeded then send the email to the 
    user associated 
    """
    over_spend_ads = []
    user = User.objects.get(id=user_id)
    access_token = Creds.objects.get(user=user).LONGLIVED_ACCESS_TOKEN
    ads = AdRecord.objects.filter(user=user,is_active=True, expired=False).all()
    today = datetime.now()
    today_date = today.strftime("%Y-%m-%d")
    last_month = today - timedelta(days=30)
    last_month_date = last_month.strftime("%Y-%m-%d")
    
    for ad in ads:
        url =  f'https://graph.facebook.com/v18.0/{ad.ad_id}/insights?fields=spend&time_range[since]={last_month_date}&time_range[until]={today_date}&access_token={access_token}'
        try:
            response = requests.get(url=url)
        except Exception as e:
            # print(e)
            pass
        content = response.json()
        spend = content['data'][0]['spend'] if len(content['data']) > 0 else 0
        ad.ad_spend = spend
        ad.is_limit_set = True
        ad.save()
        if float(spend) > ad.ad_spend_limit and ad.is_limit_set == True and ad.ad_spend_limit  != 0.0:
            over_spend_ads.append(ad)
            ad.expired = True
            ad.save()
        print(ad.ad_name, ad.ad_spend, ad.ad_spend_limit)
        
    return (over_spend_ads, user.email)


def send_limit_exceed_mail(adlist, user_email):
    """
    Send remider email to user if 
    ad spend limit has exceeded 
    """ 
    if len(adlist) != 0:
        msg_html = render_to_string('email_template/spend_limit.html', 
                                    {'adlist': adlist})

        send_mail(
            'Ad Spend limit reached!',
            "Check belows Ads that have surpassed the spend limit!",
            settings.EMAIL_HOST_USER,
            [ user_email,],
            html_message=msg_html,
        )
