from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from urllib.request import urlopen
import time 
from textblob import TextBlob
import urllib.request 
import json
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage, get_connection, send_mail, send_mass_mail
from django.conf import settings
import requests 
import plotly.offline as opy
import plotly.graph_objs as go
from access_token import USER_LONGLIVED_ACCESS_TOKEN
from .models import Creds, AccountPages, AccountsAd, ContactUs
from .sentiment_graph import get_sentiment_graph
from .utils import (
    get_account_name, get_account_post_list,
    get_post_comment_count, get_post_photos, 
    comment_info, get_permission_list, 
    get_long_lived_access_token, valid_permission_list, PageAndAccountToken
)
from .decorator import custom_login_required


@custom_login_required
def get_accounts(request):
    access_token = Creds.objects.get(user=request.user).LONGLIVED_ACCESS_TOKEN
    url = f"https://graph.facebook.com/v16.0/me/accounts?access_token={access_token}"
    accounts_json = json.loads(urllib.request.urlopen(url).read())
    accounts = accounts_json['data']
    context = {
        "accounts":accounts
    }

    return render(request, "facebook_accounts/facebook_accounts.html", context)


@custom_login_required
def sentiment_graph_posts(request, account_id, account_access_token):
    post_id_list = get_account_post_list(account_id=account_id, account_access_token=account_access_token)
    account_name = get_account_name(acc_id=account_id, access_token=account_access_token)
    graph_container = []
    for post_id in post_id_list:
        comment_count = get_post_comment_count(post_id, account_access_token)
        if comment_count > 0:
            graph = get_sentiment_graph(effective_object_story_id=post_id, access_token=account_access_token, post_title="No Title Available" )
            try:
                picture_url = get_post_photos(post_id=post_id, page_access_token=account_access_token)
            except Exception as e:
                # print(e)
                picture_url = ""
            graph['full_picture_url'] = picture_url
            graph['access_token'] = account_access_token
            graph_container.append(graph)
            # random_number = 4
    context = {
                "graph_container":graph_container,
                "adset_name":account_name,
                "adset_id":account_id, 
                # "random_number": random_number
            }
    if len(graph_container) ==0:
            messages.info(request, "We couldn't find any comment in this Facebook account!")
            context.update({"no_comments":True})

    return render(request, "facebook_accounts/sentiment_graph.html", context)


@custom_login_required
def Post_hide_comment(request, account_id, comment_id, account_access_token):
    url = f'https://graph.facebook.com/{comment_id}'
    data = {
        'is_hidden': 'true',
        'access_token': account_access_token
    }
    # print("comment and access token \n",comment_id,"\n", account_access_token)
    response = requests.post(url, data=data)
    if response.status_code == 200:
        comment_message = comment_info(comment_id, access_token=account_access_token)
        messages.success(
            request, 
            "Your request was successful. \nComment : `{}` is hidden now from users.".format(comment_message)
            )
    else:
        # print(response.text)
        messages.error(request, "Request Failed! {}".format(response.text))
    return HttpResponseRedirect(
        reverse('sentiment-graph-post', 
        kwargs={'account_id': account_id, "account_access_token":account_access_token}))


@custom_login_required
def Post_unhide_comment(request, account_id, comment_id, account_access_token):
    url = f'https://graph.facebook.com/{comment_id}'
    data = {
        'is_hidden': 'false',
        'access_token': account_access_token
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        comment_message = comment_info(comment_id, access_token=account_access_token)
        messages.success(
            request, 
            "Your request was successful. \nComment : `{}` is unhidden now from users.".format(comment_message)
            )
    else:
        # print(response.text)
        messages.error(request, "Request Failed! {}".format(response.text))
    return HttpResponseRedirect(
        reverse('sentiment-graph-post', 
        kwargs={'account_id': account_id, "account_access_token":account_access_token}))


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# saving app credentials with access token

# @custom_login_required
def save_app_credentials(request):
    if request.method == "POST":
        app_id = request.POST['app_id']
        app_secret = request.POST['app_secret']
        if app_id == "" or app_secret == "":
            messages.error(request, "Please provide valid details.")
            return render(request, "register_token/APP_ID_form.html")
        # if len(app_id) != 15 or len(app_secret) != 32:
        #     print("Please check your creadentials again")
        #     return render(request, "APP_ID_form.html")
        try:
            creds = Creds()
            creds.APP_ID = app_id
            creds.APP_SECRET = app_secret 
            creds.has_app_key = True
            creds.user = request.user
            creds.save() 
            print(app_id, " ", app_secret)
        except:
            pass
        return render(request, "register_token/APP_ACCESS_TOKEN_form.html")
    return render(request, "register_token/APP_ID_form.html")


def save_access_token(request):
    if request.method == "POST":
        access_token = request.POST['access_token']
        print(access_token)
        permission_list = get_permission_list(token=access_token)
        # try:
        #     permission_list = get_permission_list(token=access_token)
        # except Exception as e:  # handle 400 from facebook
        #     print(e)
        #     pass
        #     return redirect('save-access-token')  # redirect user to access token page
        missing_permissions = [a for a in valid_permission_list if a not in permission_list]
        print("VALID PERMISSIONS   ::::: {}".format(valid_permission_list))
        print("MISSING PERMISSIONS ::::: {}".format(missing_permissions))
        print("CURRENT PERMISSIONS ::::: {}".format(permission_list))
        if len(missing_permissions) == 0:
            creds = Creds.objects.get(user=request.user)
            long_lived_access_token = get_long_lived_access_token(
                creds.APP_ID, creds.APP_SECRET, 
                access_token=access_token
                )
            creds.ACCESS_TOKEN = access_token
            creds.LONGLIVED_ACCESS_TOKEN = long_lived_access_token
            creds.has_access_token = True
            creds.save()
            save_account_pages(user=request.user)
            # creds.save
            return redirect(reverse('home'))
        else:
            messages.error(request, "You have some missing permissions in the access token.")
            messages.error(request, "Make sure you have these permissions: {} also included in the access token.".format(missing_permissions))
            return render(request, "register_token/APP_ACCESS_TOKEN_form.html")
    else: 
        # print("lll")
        return render(request, "register_token/APP_ACCESS_TOKEN_form.html")
    


def save_account_pages(user):
    creds = Creds.objects.get(user=user)
    api_key = creds.APP_ID
    api_secret = creds.APP_SECRET
    token = creds.LONGLIVED_ACCESS_TOKEN
    pages = PageAndAccountToken(access_token=token)
    page_objects = []
    for p in pages:
        # if page exists then edit page access token 
        acc_page_ = AccountPages.objects.filter(page_id=p['id'])
        if acc_page_.exists():
            acc_page_ = AccountPages.objects.get(page_id=p['id'])
            acc_page_.page_access_token = p['access_token']
            acc_page_.longlived_access_token = get_long_lived_access_token(
                                            api_key=api_key, api_secret=api_secret, 
                                            access_token=p['access_token'])
            acc_page_.save()
        else:
            acc_page = AccountPages()
            acc_page.user = user
            acc_page.page_name = p['name']
            acc_page.page_id = p['id']
            acc_page.page_access_token = p['access_token']
            acc_page.longlived_access_token = get_long_lived_access_token(
                                                api_key=api_key, api_secret=api_secret, 
                                                access_token=p['access_token'])
            acc_page.has_access_token = True
            page_objects.append(acc_page)
        # print("saved {} with Id {}".format(p['name'], p['id']))
    if len(page_objects) != 0:
        AccountPages.objects.bulk_create(page_objects)


# Landing page to set up api keys 
def description(request):
    return render(request, "register_token/APP_create_facebook_app.html")

@custom_login_required
def contact_us(request):
    if request.method == "POST":
        user = request.user
        message = request.POST['message']
        phone = request.POST['phone']
        # print(message, "\n", phone)
        send_mail(
            'Message from Sentiment App user.',
            f"""Message from Sentiment App user!\n
            User details:
            Username: {user.username}
            Email: {user.email}
            Contact: {phone}
            Message: {message}""",
            settings.EMAIL_HOST_USER,

            ['kundan.k.pandey03@gmail.com',],#"georgeyoumansjr@gmail.com","coboaccess2@gmail.com",],
            )
        send_mail(
            "We are reviewing your query!",
            "Hi, thanks for reaching out to us! Our developers are notified of the problem, and they will get back to you shortly. Best Regards!",
            settings.EMAIL_HOST_USER,
            [request.user.email,],
            # ["kundanpandey.dev@gmail.com"]
        )
        #note save the contact made in db
        #send an email to user with contact confirmation (template)
        #send an email to self (template)
        cu = ContactUs()
        cu.user = request.user 
        cu.phone = phone
        cu.message = message 
        cu.save()
        messages.info(request, "Thank you for reaching out to us. We will get back to you shortly.")
        return render(request, "contact_us.html")
        # return redirect("/")
    else:
        return render(request, "contact_us.html")



# @custom_login_required
# def token_expired(request):
#     if request.method == "POST":
#         access_token = request.POST['access_token'] # user access token 
#         user = request.user
#         #renew user token with page token and also update tokens for adaccounts 

#         return redirect("home")
#     else:
#         return render(request, "register_token/token_expired.html")