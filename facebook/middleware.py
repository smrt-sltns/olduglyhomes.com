from django.shortcuts import redirect
from .models import Creds, AccountPages, AccountsAd
import requests
import json 
from .token_expired import send_mail_token_expired


#middleware for these prefix 
url_path_for_fb = [
    "/adsets/",
    "/set-ad-accounts/",
    '/sentiment-graph/',
    "/hide_comments/",
    "/unhide_comments/",
    "/my-accounts/",
    "/account-analysis/",
]
error_codes_limit_reached = [4, 17, 32, 613]
error_code_expired = [190]

#condition for token to give 400 response 
# api response limit is exauhsted 
# page token is invalid 
# user token is invalid or expired (middleware only apply to this )

#renew the page token if expired 
#redirect to token_expired page if User token is expired (critical)
class TokenExpiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # print("from custom middleware",response.status_code, request.path)
        request_path_prefix = str(request.path).split("/")
        # print(request_path_prefix)
        if f"/{request_path_prefix[1]}/" in url_path_for_fb:
            if response.status_code >= 400:
                limit, expired = test_user_access_token(request)
                if limit:
                    print("user token limit reached")

                if expired:
                    send_mail_token_expired(request.user.email)
                    print("user token is expired")
                return redirect('token-expired') 
        return response
    


# user access token test  
def test_user_access_token(request):
    access_token = Creds.objects.get(user=request.user).LONGLIVED_ACCESS_TOKEN
    url = f"https://graph.facebook.com/v16.0/me/accounts?access_token={access_token}"
    expired = False
    limit_reached = False
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print("Error making the request:", e)
        error_data = response.json()
        error_message = error_data.get('error', 'Unknown Error')
        # print(error_message)
        # print(error_message['code'])
        print(F"ERROR CODE : {error_message['code']}")
        if error_message['code'] in error_codes_limit_reached:
            limit_reached = True
        if error_message['code'] in error_code_expired:
            expired = True
    return limit_reached, expired 


def test_page_token_for_adaccount(request):
    # adaccounts = AccountsAd.objects.filter(user)
    pass 


