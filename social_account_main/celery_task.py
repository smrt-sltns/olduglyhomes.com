import django 
django.setup()
from celery import Celery, shared_task
from django.conf import settings 
from django.core.mail import EmailMessage, get_connection, send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.conf import settings
import os
from facebook.models import AccountsAd
from facebook.token_expired import renew_access_token
from facebook.new_pages import save_new_fb_pages

from .emails import (negative_comment_today, positive_comments_send_email, save_ads, 
                    save_campaings, save_comments, negative_comments_send_email)
from .myads_utils import email_to_file_name
from automation.models import LogNegativeComments, LogPositiveComments
from limit.task import spend_limit_and_email, capture_new_ads



# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_account_main.settings')
app = Celery('social_account_main')
app.config_from_object('django.conf:settings', namespace='CELERY')

from celery.signals import setup_logging

@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

ad_account = "act_296865963" # smart solutions account 




@app.task(bind=True)
def do_stuff(self):
    print(f'Request: {self.request!r}')


@shared_task
def send_mail_token(title, message, email_temaplate, user_email:list, **kwargs):
    msg_html = render_to_string(email_temaplate, kwargs)
    try:
        send_mail(
            title,
            message,
            settings.EMAIL_HOST_USER,
            [user_email,],
            html_message=msg_html,
            )
    except Exception as e:
        print(e)
        pass 

@shared_task
def wraped_comments(file_name,
                    account_id, 
                    token):
    # print("wrapper executed")
    save_campaings(file_name=file_name,account_id=account_id, token=token)
    save_ads(file_name=file_name, token=token)
    save_comments(file_name=file_name, token=token)


@shared_task
def LOG_negative_comments(user_id, account_id, data, is_mail_sent):
    user = User.objects.get(id=user_id)
    account = AccountsAd.objects.get(ad_account_id=account_id)
    for d in data:
        negative_log = LogNegativeComments(
            user=user, adaccount=account,
            comment=d['comment'], comment_id=d['comment_id'],
            ad_name = d['ad_name'], ad_id = d['ad_id'],
            adset_name = d['adset_name'], adset_id = d['adset_id'],
            campaign_name = d['campaign_name'], campaign_id=d['campaign_id'], 
            created_time = d['created_time'],
            is_mail_sent = is_mail_sent
        )
        negative_log.save()

@shared_task
def LOG_positive_comments(user_id, account_id, data, is_mail_sent):
    user = User.objects.get(id=user_id)
    account = AccountsAd.objects.get(ad_account_id=account_id)
    for d in data:
        positive_log = LogPositiveComments(
            user=user, adaccount=account,
            comment_count=d['count'],
            ad_name = d['ad_name'], ad_id = d['ad_id'],
            adset_name = d['adset_name'], adset_id = d['adset_id'],
            campaign_name = d['campaign_name'], campaign_id=d['campaign_id'], 
            created_time = d['created_time'],
            is_mail_sent = is_mail_sent
        )
        positive_log.save()


#every 2 hours 
@shared_task
def task_every_2_hours():
    users = User.objects.filter(is_superuser=False).all()
    for u in users:
        negative_comments_today_send_email.delay(u.id)
        capture_new_ads.delay(user_id=u.id)


@shared_task
def task_every_1_day():
    users = User.objects.filter(is_superuser=False).all()
    for u in users:
        postive_comments_yesterday_send_email.delay(u.id)
        renew_access_token(user_id=u.id)
        

@shared_task
def task_spend_limit():
    users = User.objects.filter(is_superuser=False).all()
    for u in users:
        spend_limit_and_email.delay(user_id=u.id)
    

@shared_task
def task_save_new_fb_pages():
    "Runs every day to save new facebook pages of the users in db."
    save_new_fb_pages()

#EVERYDAY
@app.task()
def postive_comments_yesterday_send_email(user_id): # works every day in the morning 
    try: 
        user = User.objects.get(id=user_id)
    except Exception as e:
        print(e)
        # print("Automation failed for user id : ".format(user_id))
    email = user.email 
    # print(email)
    f_name = email_to_file_name(email)
    ad_accounts  = AccountsAd.objects.filter(user=user)
    for ad in ad_accounts: # run automation for all the ad accounts 
        token = ad.access_token 
        account_id = ad.ad_account_id 
        account_name = ad.ad_account_name 
        folder_path = os.path.join(settings.BASE_DIR, f"JSON/{f_name}")
        if not os.path.exists(folder_path):
            os.mkdir(folder_path) #create user forlder 
        file_name = f"{folder_path}/{account_name}_{f_name}.json"
        data = {
            "file_name":file_name,
            "email": email,
            "account_name": account_name
            }
        # print(data)
        wraped_comments(file_name=file_name, account_id=account_id, token=token)
        is_mail_sent, data = positive_comments_send_email(user_email=email, file_name=file_name)
        if len(data) != 0:
            LOG_positive_comments(
                user_id=user_id, account_id=account_id, 
                is_mail_sent=is_mail_sent, data=data)

#every 2 hours 
@app.task()
def negative_comments_today_send_email(user_id): # 
    try: 
        user = User.objects.get(id=user_id)
    except Exception as e:
        print(e)
        # print("Automation failed for user id : ".format(user_id))
    # ***important 
    # make a cutomusermodel and set email field null=False, blank=False
    email = user.email 
    f_name = email_to_file_name(email)
    ad_accounts  = AccountsAd.objects.filter(user=user)
    for ad in ad_accounts:
        token = ad.access_token 
        account_id = ad.ad_account_id 
        account_name = ad.ad_account_name 
        folder_path = os.path.join(settings.BASE_DIR, f"JSON/{f_name}")
        if not os.path.exists(folder_path):
            os.mkdir(folder_path) # create a folder dedicated to each user
        file_name = f"{folder_path}/{account_name}_{f_name}.json"
        user_data = {
            "file_name":file_name,
            "email": email,
            "account_name": account_name
            }
        # print(user_data)
        wraped_comments(file_name=file_name, account_id=account_id, token=token)
        is_mail_sent, data = negative_comments_send_email(user_email=email, file_name=file_name)
        if len(data) != 0:
            LOG_negative_comments.delay(
                user_id=user_id, account_id=account_id, 
                data=data, is_mail_sent=is_mail_sent)
            # print("NEGATIVE LOG SAVED!")

