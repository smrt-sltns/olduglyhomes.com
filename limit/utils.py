import json 
import requests
import urllib.request
from decouple import config 

LONGLIVED_ACCESS_TOKEN = config("USER_LONGLIVED_ACCES_TOKEN", "")

def save_campaings(account_id="act_296865963", token=LONGLIVED_ACCESS_TOKEN):
    data = []
    campaigns = {}
    all_campaigns_url = f"https://graph.facebook.com/v16.0/{account_id}/campaigns?fields=id,name,effective_status&access_token={token}"
    all_campaigns = json.loads(urllib.request.urlopen(all_campaigns_url).read())
    for c in all_campaigns['data']:
        if c['effective_status'] == "ACTIVE":# or c['effective_status'] == "PAUSED":
            campaigns = {
                "campaign_name": c['name'], 
                "campaign_id": c['id'],  
                "campaign_status": c['effective_status'], 
                "adsets":[]
                }
            data.append(campaigns)
    # with open(file_name, 'w') as json_file:
    #     json_objects = json.dumps(data, indent=4)
    #     json_file.write(json_objects)
    return data


# save adsets and ads from the campaigs 
def save_ads(token=LONGLIVED_ACCESS_TOKEN):
    # active_campaing_list = json.loads(open(file_name, "r").read())
    active_campaing_list = save_campaings()
    
    data = []
    for c in active_campaing_list:
        adsets_url = f"https://graph.facebook.com/v16.0/{c['campaign_id']}/adsets?fields=name,id&access_token={token}"
        adsets = json.loads(urllib.request.urlopen(adsets_url).read())
        for adset in adsets['data']:
            adset_id = adset['id']
            adset_name = adset['name']
            ads_url = f"https://graph.facebook.com/v16.0/{adset['id']}/ads?fields=name,id,effective_status,creative.fields(effective_object_story_id),insights.fields(actions)&access_token={token}"
            ads_json = json.loads(urllib.request.urlopen(ads_url).read())
            ads = []
            if len(ads_json['data']) !=0:
                for a in ads_json['data']:
                    status = a['effective_status']
                    eff = a['creative']['effective_object_story_id']
                    if status == "ACTIVE":
                        ads.append({"ad_name": a['name'], "ad_id": a['id'], "status":status, 
                                    "eff":eff, "negative_comments":[], "positive_comments":[] })
                c['adsets'].append({"adset_name": adset_name, "adset_id": adset_id, "ads": ads})
        data.append(c)
    # with open(file_name, 'w') as json_file:
    #     json_objects = json.dumps(data, indent=4)
    #     json_file.write(json_objects)
    print("ads saved")
    return data 
    


def email_to_file_name(email):
    break_at = str(email).split("@")[0]
    if "." in break_at:
        join_ = "_".join(break_at.split("."))
        return  join_
    else:
        return  break_at

if __name__ == '__main__':
    # save_campaings()
    ads = save_ads()
    print(ads)