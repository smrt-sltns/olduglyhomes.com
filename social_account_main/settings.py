from pathlib import Path
from decouple import config,Csv
from celery.schedules import crontab

import os 
from datetime import timedelta
import logging.config
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = config("BASE_URL","")
# BASE_URL = "https://127.0.0.1:8000"
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-acj1g@4&c&pkah!1il$ooqm669#s@!4bag*_lw66cga8_mzqhn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", False)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

ALLOWED_HOSTS = ['190.92.151.242', "www.smarttextinfo.com", "smarttextinfo.com", "127.0.0.1"]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.sites",
    'facebook',
    "automation",
    "youtube",
    # 'social_django',
    "limit",
    
    # force https on social-oauth 
    # 'sslserver',
    'django_celery_results',
    
    # all auth configurations
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # social django middleware 
    'social_django.middleware.SocialAuthExceptionMiddleware',
    # Custom middleware if User token is expired 
    "facebook.middleware.TokenExpiredMiddleware",
    #all auth 
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'social_account_main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'template')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # social django templates 
                'social_django.context_processors.backends',  
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'social_account_main.wsgi.application'

SITE_ID = 3
# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}
LOGIN_REDIRECT_URL = "success"
SOCIALACCOUNT_LOGIN_ON_GET = True  # This shows google's authorization page, skipping a sign-in page that pops up
SOCIALACCOUNT_AUTO_SIGNUP = True   # This automatically signs up a user after using google to sign in
ACCOUNT_LOGOUT_ON_GET = True
LOGOUT_REDIRECT_URL = "sign-in"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]




# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LOGGING_DIR = os.path.join(BASE_DIR, 'logs')  # Directory to store log files

if not os.path.exists(LOGGING_DIR):
    os.makedirs(LOGGING_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'celery': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'celery.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'celery': {
            'handlers': ['celery'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# media files 
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'uploads'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 2

LOGIN_REDIRECT_URL= "youtube-index"
LOGOUT_REDIRECT_URL = "home"



AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
 
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
)

# AUTHENTICATION_BACKENDS = (
#     'allauth.account.auth_backends.AuthenticationBackend',
#     'django.contrib.auth.backends.ModelBackend',
# )

# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',
    
# ]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional' 


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config("GOOGLE_CLIENT_ID"),
            'secret': config("GOOGLE_CLIENT_SECRET")    ,
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


SOCIAL_AUTH_FACEBOOK_KEY = config('APP_ID')
SOCIAL_AUTH_FACEBOOK_SECRET = config('APP_SECRET')
# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "your_google_clientId"
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "your_google_clientsecret"



SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,name,email', 
}

FACEBOOK_API_VERSION = config("FACEBOOK_API_VERSION")
TUT  = "https://medium.com/@namantam1/login-with-facebook-and-google-in-django-using-social-auth-app-django-d042bfeb04cb"




# #SMTP SERVER BACKENT
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mail.ger-rei.com'
# EMAIL_USE_TLS = False
# EMAIL_PORT = 465
# EMAIL_USE_SSL = True
# EMAIL_HOST_USER = 'contact@ger-rei.com'
# EMAIL_HOST_PASSWORD = 'Ohappydays@1'


#gmail smtp setup 
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "coboaccess2@gmail.com" 
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = 'coboaccess2@gmail.com'

CONTACT_US_EMAIL = "kundan.k.pandey03@gmail.com" # we listen to users on this email


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}

CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'

CELERY_CACHE_BACKEND = 'default'

CELERY_TIMEZONE = "Asia/Kolkata"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# celery beat to run task every x time 
CELERY_BEAT_SCHEDULE = {

#----------------------------------------------------------------------FACEBOOK--------------------------------------------------------------------

      'add-every-1-day': {
        'task': 'social_account_main.celery_task.task_every_1_day',
        'schedule': timedelta(days=1),
        'args': '',
        'options': {
            'expires': 120.0,
        },
      },


      'add-every-2-hours': {
        'task': 'social_account_main.celery_task.task_every_2_hours',
        'schedule': timedelta(hours=1),
        'args': '',
        'options': {
            'expires': 150.0,
        },
      },
      
      'task_save_new_fb_pages': {
        'task': 'social_account_main.celery_task.task_save_new_fb_pages',
        'schedule': timedelta(days=1),
        'args': '',
        'options': {
            'expires': 300.0,
        },
      },
      
      #update ads spend every 10 min 
      'task_spend_limit': {
        'task': 'social_account_main.celery_task.task_spend_limit',
        'schedule': timedelta(minutes=20),
        'args': '',
        'options': {
            'expires': 150.0,
        },
      },
      
#----------------------------------------------------------------------YOUTUBE--------------------------------------------------------------------
      
      'task_youtube_subs_count': {
        'task': 'youtube.tasks.task_save_video',
        'schedule': timedelta(minutes=10),
        
        'args': "",
        'options': {
            'expires': 150.0,
        },
      },

    # #SAP
    #   'task_youtube_subs_count': {
    #     'task': 'youtube.tasks.task_save_video',
    #     'schedule': timedelta(minutes=10),
    #     'args': ('SAP',),
    #     'options': {
    #         'expires': 150.0,
    #     },
    #   },

    
}
