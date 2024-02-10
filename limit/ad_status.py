import requests 
from facebook.utils import get_ad_id_list
from django.conf import settings 




def set_ad_status(access_token, ad_id, status):
    print("Switching to : ", status)
    ad_set_endpoint = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{ad_id}"
    params = {
        'status': status, 
        'access_token': access_token,
    }
    try:
        response = requests.post(ad_set_endpoint, params=params)
        response_data = response.json()
        if 'success' in response_data and response_data['success']:
            print(f"Ad with ID {ad_id} {status} successfully.")
            result = True
        else:
            print(f"Failed to {status} ad with ID {ad_id}. Error: {response_data.get('error', 'Unknown error')}")
            result = True
    except requests.RequestException as e:
        print(f"Error making request: {e}")
        result = False
    return result 


def set_campaign_status(access_token, campaign_id, status):
    campaign_ad_list = get_ad_id_list(campaign_id=campaign_id, access_token=access_token)
    #pause all the ads in the campaign 
    for ad_id in campaign_ad_list:
        result = set_ad_status(ad_id=ad_id, access_token=access_token, status=status)
        
    #pause the campaign
    result = set_ad_status(ad_id=campaign_id, access_token=access_token, status=status)
    #if result is true then all the requests made were successfull 
    return result 