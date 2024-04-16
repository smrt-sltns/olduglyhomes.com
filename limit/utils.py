import json 
import requests
import urllib.request
from decouple import config 
from django.contrib.auth.models import User 
from django.conf import settings
from .models import AdRecord
from datetime import datetime, timedelta



def adrecord_groups(adrecords):
    if len(adrecords) == 0:
        return {}
    
    ad_records_by_campaign = {}
    for ad_record in adrecords:
        campaign_name = ad_record.campaign_name
        campaign_id = ad_record.campaign_id
        adset_name = ad_record.adset_name
        adset_id = ad_record.adset_id

        if campaign_id not in ad_records_by_campaign:
            ad_records_by_campaign[campaign_id] = {
                "campaign_data": ad_record, 
                "adsets" : {}
            }
        if adset_id not in ad_records_by_campaign[campaign_id]['adsets']:
            ad_records_by_campaign[campaign_id]['adsets'][adset_id] = {
                'adset_id': ad_record.adset_id,  
                "adset_name": ad_record.adset_name,
                'adset_spend': ad_record.adset_spend,  
                
                "adrecords" : []
            }
        ad_records_by_campaign[campaign_id]['adsets'][adset_id]['adrecords'].append(ad_record)
    return ad_records_by_campaign


def email_to_file_name(email):
    break_at = str(email).split("@")[0]
    if "." in break_at:
        join_ = "_".join(break_at.split("."))
        return  join_
    else:
        return  break_at


def one_month_old_dates(days_old=30):
    today = datetime.now()
    today_date = today.strftime("%Y-%m-%d")
    last_month = today - timedelta(days=days_old)
    last_month_date = last_month.strftime("%Y-%m-%d")
    print(today_date, last_month_date)
    return today_date, last_month_date

