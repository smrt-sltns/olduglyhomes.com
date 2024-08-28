from django.conf import settings 
import os 

"""This directory contains the auth token file that expires every 7 days."""


class CredFile:
    base_url = settings.BASE_URL    
    CREAD_SAP = os.path.join(base_url, "youtube/Analytics/creadFile/SAP.json")
    CREAD_SOFT_MARKETING = os.path.join(base_url, "youtube/Analytics/creadFile/SOFT_MARKETING.json")