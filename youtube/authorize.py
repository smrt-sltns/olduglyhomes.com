from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import redirect
import jwt 
import requests
from django.conf import settings 


def index(request):
    return HttpResponse("Home!!")


def google_auth(request):
    google_login_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        "scope=email%20profile%20https://www.googleapis.com/auth/youtube.readonly" 
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        "&access_type=offline"
    )
    return redirect(google_login_url)


def google_auth_callback(request):
    authorization_code = request.GET.get('code', None)
    if authorization_code:
        all_token = requests.post(
            'https://www.googleapis.com/oauth2/v4/token',
        data = {
            'code': authorization_code,

            'grant_type': 'authorization_code',
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        }).json()
        # print(all_token)
        # id_token = all_token['id_token']
        # refresh_token = all_token['refresh_token']
        # decode_token = jwt.decode(id_token, algorithms=['RS256'], verify=False)
        print("ACCESS TOKEN : {}".format(all_token['access_token']))
        # print("REFRESH TOKEN : {}".format(refresh_token))
        # print("ID TOKEN : {}".format(id_token))
        # print("DECODED ID TOKEN :: {}".format(decode_token))
        # print("EMAIL : {}".format(decode_token['email']))
        # print("NAME : {}".format(decode_token['name']))
        return HttpResponse('Spreadsheet created successfully')
    return HttpResponse('Authentication failed code missing ')