from django.shortcuts import redirect, render 
from django.http import HttpResponse
from .utils import PageAndAccountToken, get_long_lived_access_token, get_permission_list, get_all_campaigns
from .models import Creds, AccountPages, AccountsAd
from .decorator import custom_login_required
# from social_account_main.token_renew import renew_access_token
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from .views import save_account_pages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection, send_mail, send_mass_mail
from django.conf import settings
import smtplib


CONTACT_EMAILS = [ "kundanpandey.dev@gmail.com", "georgeyoumansjr@gmail.com","coboaccess2@gmail.com"]
# ['kundan.k.pandey02@gmail.com',
                #  
                # ],

@custom_login_required
def token_expired(request):
    if request.method == "POST":
        access_token = request.POST['access_token'] # user access token 
        user = request.user
        #renew user token with page token and also update tokens for adaccounts 
        longlived_access_token = get_long_lived_access_token(
            api_key=user.creds.APP_ID, 
            api_secret=user.creds.APP_SECRET,
            access_token=access_token)
        # print("longlived access token: ",longlived_access_token)
        cred = Creds.objects.get(user_id=request.user.id)
        cred.LONGLIVED_ACCESS_TOKEN = longlived_access_token
        cred.save()
        renew_access_token(user_id = request.user.id, date_required=False) #take user token and renew all the token related to the user 
        return redirect("home")
    else:
        adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
        context = {
                "adaccount_is_set":adaccount_is_set,
            }
        if adaccount_is_set:
            adaccounts = AccountsAd.objects.filter(user=request.user).all()
            context['adaccounts'] = adaccounts
        return render(request, "register_token/token_expired.html", context)



@custom_login_required
def token_expired_page(request):
    renew =  request.GET.get("renew", None)
    if renew != None:
        user_id = request.user.id 
        renew_access_token(user_id=user_id, date_required=False)
        return redirect("home")
    else:
        adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
        context = {
                "adaccount_is_set":adaccount_is_set,
            }
        if adaccount_is_set:
            adaccounts = AccountsAd.objects.filter(user=request.user).all()
            context['adaccounts'] = adaccounts
        return render(request, "register_token/token_expired_page.html", context)



@custom_login_required
def token_limit_reached(request):
    adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
    context = {
            "adaccount_is_set":adaccount_is_set,
        }
    if adaccount_is_set:
        adaccounts = AccountsAd.objects.filter(user=request.user).all()
        context['adaccounts'] = adaccounts
    return render(request, "register_token/token_limit_reached.html", context)



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
    # print(status)
    return status


def renew_access_token(user_id, date_required=True):
    user = User.objects.get(id=user_id)
    cred = Creds.objects.get(user=user)
    if date_required:
        status = is_datefield_one_month_old(cred)
    else:
        status = True
    if status:
        token = cred.LONGLIVED_ACCESS_TOKEN
        api_key = cred.APP_ID
        api_secret = cred.APP_SECRET
        long_lived_token = get_long_lived_access_token(api_key=api_key, api_secret=api_secret,access_token=token)
        cred.ACCESS_TOKEN = token 
        cred.LONGLIVED_ACCESS_TOKEN = long_lived_token # renew access token for creds models
        cred.create_date = timezone.now().date()
        cred.save()  
        # print(f"Renewed Access token for {user.email}")
        save_account_pages(user=user) # renew access token for all the pages 

        adaccounts = AccountsAd.objects.filter(user=user)
        for ad in adaccounts:
            page_token = ad.page_associated.longlived_access_token
            ad_token = ad.access_token
            if page_token != ad_token:
                ad.access_token = page_token # changing access token of the ad account 
                ad.save()
                print(f"Access token of {ad.ad_account_name} is changed!" )
    else:
        print("ACCESS TOKEN STATUS : ", status)


def remove_old_access_token(request):
    cred = Creds.objects.get(user=request.user)
    cred.has_access_token = False
    cred.save()
    return redirect("home")


def send_mail_token_expired(user_email):
    user = User.objects.get(email=user_email)
    user_html = render_to_string('email_template/token_expired.html', 
                                    {'user': user})
    self_html = render_to_string("email_template/token_expired_self.html", {"user":user})
    mail_sent = False
    try:
        send_mail(
            'Access Token Expired',
            "Please renew your Access Token!",
            settings.EMAIL_HOST_USER,
            [user_email, ],
            html_message=user_html,)
        send_mail(
            'Access Token Expired',
            f"Access Token of the user {user.email} has Expired!",
            settings.EMAIL_HOST_USER,
            CONTACT_EMAILS,
            html_message=self_html,)
        mail_sent = True
        print("MAIL SENT. User Access Token expired!")
    except smtplib.SMTPException as e:
        print(e)


def send_mail_token_limit_reached(user_email):
    user = User.objects.get(email=user_email)
    user_html = render_to_string('email_template/token_limit_reached.html', 
                                    {'user': user})
    mail_sent = False
    try:
        send_mail(
            'Access Token Limit reached',
            "You have exhausted you Facebook API call limit!",
            settings.EMAIL_HOST_USER,
            [user_email,],
            html_message=user_html,)
        mail_sent = True
        print("MAIL SENT. User Access Token expired!")
    except smtplib.SMTPException as e:
        print(e)


