from django.conf import settings 
import os 

"""This directory contains credential json file generated from google console."""


class TokenFile:
    base_url = settings.BASE_URL    
    TOKEN_SAP = os.path.join(base_url, "youtube/Analytics/creadFile/SAP.pickle")
    TOKEN_SOFT_MARKETING = os.path.join(base_url, "youtube/Analytics/creadFile/SOFT_MARKETING.pickle")