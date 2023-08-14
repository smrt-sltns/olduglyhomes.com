from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import logout
from urllib.request import urlopen
import time 
from textblob import TextBlob
import urllib.request 
import json
from django.contrib import messages
from django.http import HttpResponse
import plotly.offline as opy
import plotly.graph_objs as go
from automation.models import LogNegativeComments, LogPositiveComments
from .decorator import custom_login_required
from .models import AccountsAd, Creds
from .utils import (
    split_id, get_post_name_from_commentid, 
    get_account_name, get_campaign_name_and_id
    )




# Create your views here.
def login(request):
  return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect(reverse("home"))



@custom_login_required
def home(request):
    user = request.user
    ad = AccountsAd.objects.filter(user=user)
    if ad.exists():
        ad_id = ad[0].id
        redirect_url = reverse("negative_report", args=[ad_id])
        return redirect(redirect_url)
    else:
        adaccount_is_set = False # needs to come from database 
        context = {
            "adaccount_is_set":adaccount_is_set,
        }
        return render(request,"index.html", context)




@custom_login_required
def get_posts(request, page_id, page_access_token):
    social_user = request.user.social_auth.filter(provider='facebook').first()
    if social_user:
        accounts_posts_url = u"https://graph.facebook.com/{0}/posts?access_token={1}".format(
                        page_id,
                        page_access_token,)
        accounts_posts_json = json.loads(urllib.request.urlopen(accounts_posts_url).read())
        comments_list = []
        account_dict  = {}
        for data in accounts_posts_json['data'][:20]:
            account_comments_url = u"https://graph.facebook.com/{0}/comments?access_token={1}".format(
                                data['id'],
                                page_access_token,)
            account_comments_json = json.loads(urllib.request.urlopen(account_comments_url).read())
            comments_list +=[account_comments_json['data']]
            account_dict['comments_data'] = account_comments_json
        contain_div = []
        for com in comments_list:
            positive_sentiment = 0
            negative_sentiment = 0 
            neutral_sentiment = 0
            for c in com:
                comment_id = []
                comment_string = TextBlob(c['message'])
                comments_polarity = comment_string.sentiment.polarity
                if comments_polarity > 0.0:
                    positive_sentiment += 1
                elif comments_polarity < 0.0:
                    negative_sentiment += 1
                else:
                    neutral_sentiment += 1
                comment_id += [c['id']]
            value = [negative_sentiment, neutral_sentiment, positive_sentiment]
            names = ['Negative Comments', 'Neutral Comments', 'Positive Comments']
            account_name = get_account_name(page_id, page_access_token)
            try: 
                post_title = get_post_name_from_commentid(c['id'], account_data=accounts_posts_json['data'])
            except BaseException: 
                post_title = "NO COMMENTS YET" 
            if sum(value) != 0:  
                trace1 = go.Bar(x=names, y=value )
                data=go.Data([trace1])
                layout=go.Layout(title=post_title, xaxis={'title':'Comments'}, yaxis={'title':'Count'})
                figure=go.Figure(data=data,layout=layout, ) 
                figure.update_traces(marker_color=['red', 'blue', 'green'])             
                div = figure.to_html(
                    full_html=False, default_height=400, 
                    default_width=500,
                    config=dict(displayModeBar=False))
                contain_div += [div]
        context = {
            'posts': accounts_posts_json['data'],
            'graphs': contain_div[:10],
            'account_name':account_name,
        }
        return render(request, 'account_posts.html', context)
  

   
@custom_login_required       
def social_auth_data(request):
    social_user = request.user.social_auth.filter(provider='facebook',).first()
    print(social_user)
    if social_user:
        friend_url = u'https://graph.facebook.com/{0}/' \
            u'friends?fields=id,name,location,picture' \
            u'&access_token={1}'.format(
                social_user.uid,
                social_user.extra_data['access_token'],
            )
        me_url = u'https://graph.facebook.com/{0}?' \
            u'fields=id,name,email,location,picture,gender,birthday,likes,posts' \
            u'&access_token={1}'.format(
                social_user.uid,
                social_user.extra_data['access_token'],
            )
            
        accounts_url = u"https://graph.facebook.com/{}/accounts?"\
                        u"fields=id,name,access_token&" \
                        "access_token={}".format(
                            social_user.uid,
                            social_user.extra_data['access_token'],
                        )

    print(me_url, '\n')
    
    scope_list = ['email', 'name', 'gender', 'location', 'birthday', 'posts', 'likes',]
    # email = json.loads(urllib.request.urlopen(me_url).read()).get('email')
    accounts_page = json.loads(urllib.request.urlopen(accounts_url).read())
    
    friends = json.loads(urlopen(friend_url).read())#.get('data')
    for data in scope_list:
        data_response = json.loads(urllib.request.urlopen(me_url).read()).get(data)
        print(data_response, '\n')
    print('\n', 'Account informations','\n')
    print(accounts_page)
    print('\n', 'friends list ', '\n')
    print("page id and page name")
    for d in accounts_page['data']:
        print(d['id'], d['name'])
        print('\n')
    print(friends)
    return HttpResponse(social_user)
    
    


@custom_login_required
def get_comments(request):
    social_user = request.user.social_auth.filter(provider='facebook',).first()
    if social_user:
        # comments from the cokacola post 
        comment_url = "http://graph.facebook.com/10152297032458306/comments"
        comment_url2 = u"https://graph.facebook.com/19292868552_118464504835613/comments?fields=id" \
                        u"&access_token={}".format(social_user.extra_data['access_token'])
        
        read_comments = json.loads(urllib.request.urlopen(comment_url2).read())
        print(comment_url)
        for comm in read_comments:
            print(comm, '\n')
        return HttpResponse("done!")
    
    
    
@custom_login_required
def get_pages(request):
    social_user = request.user.social_auth.filter(provider='facebook',).first()
    if social_user:
        # comments from the cokacola post 
        pages_url = u"http://graph.facebook.com/{}/accounts&" \
                    u"access_token={}".format(social_user.uid, social_user.extra_data['access_token'])
        print(pages_url)
        read_pages = json.loads(urllib.request.urlopen(pages_url).read())
        print(read_pages)
        return HttpResponse("done")
    
@custom_login_required 
def get_page_access_token(user):
    social_user = user.social_auth.filter(provider='facebook').first()
    if social_user:
        accounts_url = accounts_url = u"https://graph.facebook.com/{}/accounts?"\
                        u"fields=id,name,access_token&" \
                        "access_token={}".format(
                            social_user.uid,
                            social_user.extra_data['access_token'],)
                        
        read_accounts_json = json.loads(urllib.request.urlopen(accounts_url).read())
        
        data = read_accounts_json['data']
        return data

    
@custom_login_required 
def get_post_and_comments_accounts(request):
    user = request.user
    data = get_page_access_token(user=user)
    # print(data)
    # if data[0]['name'] == 'Pythonsdk':
    page_access_token = data[0]['access_token']
    page_id = data[0]['id']
    accounts_posts_url = u"https://graph.facebook.com/{0}/posts?access_token={1}".format(
                        page_id,
                        page_access_token,)
    print(accounts_posts_url)
    account_post_json = json.loads(urllib.request.urlopen(accounts_posts_url).read())
    print(account_post_json['data'])
    for d in account_post_json['data']:
        account_post_id = d['id']
        account_commnets_url = u"https://graph.facebook.com/{0}/comments?access_token={1}".format(
                                account_post_id,
                                page_access_token,)
        account_commnets_json = json.loads(urllib.request.urlopen(account_commnets_url).read())
        print('comments','\n')
        print(account_commnets_json)
    print('\n')
    # print(data[0]['name'])
    # print(data[1]['name'])
    return HttpResponse("Printed access_token and name")



@custom_login_required
def user_social_data(request, *args, **kwargs):
    try:
        import urllib
    except Exception:
        from urllib3 import request
        print('cant import urllib from python 3')
        
    if not kwargs['is_new']:
        return   
    # user = kwargs['user']
    if kwargs['backend'].__class__.__name__ == 'FacebookBackend':
        fbuid = kwargs['response']['id']
        access_token = kwargs['response']['access_token']

        url = 'https://graph.facebook.com/{0}/' \
              '?fields=email,gender,name' \
              '&access_token={1}'.format(fbuid, access_token,)

        photo_url = "http://graph.facebook.com/%s/picture?type=large" \
            % kwargs['response']['id']
        request = urllib.request(url)
        response = urllib.urlopen(request).read()
        email = json.loads(response).get('email')
        name = json.loads(response).get('name')
        gender = json.loads(response).get('gender')
        context = {
            'email': email,
            'name':name,
            'gender':gender,
        }
        return render(request, 'index.html', context )
    else:
        messages.error(request, "No data from facebook backend was returned")
        return render(request, "index.html")
