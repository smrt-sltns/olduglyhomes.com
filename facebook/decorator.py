from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.messages import error, success, info
from .models import Creds, DefaultApp
from django.urls import reverse
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
from functools import wraps



def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not request.user.is_authenticated:
            info(request, "Please login to continue!")
            return render(request, "login.html")
        creds = Creds.objects.filter(user=request.user)
        # if not DefaultApp.objects.filter(user = request.user).exists():
        #     DefaultApp.objects.create(user=user)
        # default_app = DefaultApp.objects.filter(user=user).first()
        # if default_app.to_youtube == False:
        if not creds.exists():
            return render(request, "register_token/APP_create_facebook_app.html")
        try: 
            creds = Creds.objects.get(user=user)
        except Exception:
            return render(request, "register_token/APP_ID_form.html")
        if creds.has_app_key == False: #check if api keys are set 
                error(request, "You haven't set your api keys. Please provide your APP KEY and APP SECRET.")
                return render(request, 'APP_ID_form.html')
        if creds.has_access_token == False: #check if ther user has working access token
            info(request, "Please provide your access token with all the permission listed.")
            return render(request, "register_token/APP_ACCESS_TOKEN_form.html")
        return view_func(request, *args, **kwargs)
    return wrapper



def youtube_login_decorator(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not request.user.is_authenticated:
            info(request, "Please login to continue!")
            return render(request, "login.html")
        return view_func(request, *args, **kwargs)
    return wrapper