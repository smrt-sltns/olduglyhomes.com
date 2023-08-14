from access_token import LONGLIVED_ACCESS_TOKEN
import json 
import urllib.request
from textblob import TextBlob
from datetime import datetime






#Save all active campaigns 
def save_campaings(file_name="JSON/active_campaigns.json",account_id="act_296865963", token=LONGLIVED_ACCESS_TOKEN):
    data = []
    campaigns = {}
    print("Saving active campaings")
    all_campaigns_url = f"https://graph.facebook.com/v16.0/{account_id}/campaigns?fields=id,name,effective_status&access_token={token}"
    all_campaigns = json.loads(urllib.request.urlopen(all_campaigns_url).read())
    for c in all_campaigns['data']:
        if c['effective_status'] == "ACTIVE":
            campaigns = {
                "campaign_name": c['name'], 
                "campaign_id": c['id'],  
                "campaign_status": c['effective_status'], 
                "adsets":[]
                }
            data.append(campaigns)
    with open(file_name, 'w') as json_file:
        json_objects = json.dumps(data, indent=4)
        json_file.write(json_objects)
    print("Done!")


# save adsets and ads from the campaigs 
def save_ads(file_name, token=LONGLIVED_ACCESS_TOKEN):
    active_campaing_list = json.loads(open(file_name, "r").read())
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
                                    "eff":eff, "negative_comments":[] })
                c['adsets'].append({"adset_name": adset_name, "adset_id": adset_id, "ads": ads})
        data.append(c)
    with open(file_name, 'w') as json_file:
        json_objects = json.dumps(data, indent=4)
        json_file.write(json_objects)


# def get_eff(ad_id): # effective object story id of ads 
#     ad_url = f"https://graph.facebook.com/v16.0/{ad_id}?fields=id,name,effective_status,creative.fields(effective_object_story_id),insights.fields(actions)&access_token={LONGLIVED_ACCESS_TOKEN}"
#     ad_json = json.loads(urllib.request.urlopen(ad_url).read()) 
#     effective_object_story_id = ad_json['creative']['effective_object_story_id']
#     status = ad_json['effective_status']
#     return effective_object_story_id, status

# get comments from the api 
def get_comments(eff, token=LONGLIVED_ACCESS_TOKEN):
    negative_comment_list = []
    positive_comment_list = []
    comments_url = f"https://graph.facebook.com/v16.0/{eff}/comments?fields=id,message,created_time,is_hidden&summary=true&access_token={token}&limit=100&after"
    comments = json.loads(urllib.request.urlopen(comments_url).read())
    ignore_comment_list = json.loads(open("JSON/ignored_comments.json", "r").read())
    if len(comments['data']) > 0:
        for c in comments['data']:
            is_ignored = True if c['id'] in ignore_comment_list else False
            comment_polarity = TextBlob(c['message']).sentiment.polarity
            if comment_polarity < 0.0: # negative comments 
                negative_comment_list.append(
                    {
                     "comment": c['message'], "id": c['id'], "is_hidden": c['is_hidden'], 
                     "is_ignored":is_ignored, "created_time":c['created_time'],
                     })   
            elif comment_polarity >= 0.0: # positive comments 
                positive_comment_list.append(
                    {
                     "comment": c['message'], "id": c['id'], "is_hidden": c['is_hidden'], 
                     "is_ignored":is_ignored, "created_time":c['created_time'],
                     })
    return negative_comment_list, positive_comment_list



def save_comments(file_name):
    campaigns = json.loads(open(file_name, "r").read())    
    for camps in campaigns:
        for adset in camps['adsets']:
            for ad in adset['ads']:
                if ad['status'] == "ACTIVE":
                    eff = ad['eff']
                    negative_comments_list, positive_comments_list = get_comments(eff)
                    ad['negative_comments'] = negative_comments_list
                    ad['positive_comments'] = positive_comments_list
    with open(file_name, 'w') as json_file: 
        json_object = json.dumps(campaigns, indent=4)
        json_file.write(json_object)
    print("Active campaign json file is updated with negative comments!")


def Comment_made_today(created_time:str):
    created_date = created_time.split("T")[0]
    today = datetime.now().date()
    if str(created_date) == str(today):
        return True
    else:
        return False

def Comment_made_yesterday(created_time:str):
    date = datetime.now().day
    month = datetime.now().month
    yesterday = date - 1
    created_date_ = created_time.split("T")[0]
    created_date, created_month = int(created_date_.split('-')[-1]), int(created_date_.split('-')[-2])
    if created_date == yesterday and month == created_month:
        result = True
    else: 
        result = False
    return result 


def get_grouped_list(data):
    print(data)
    grouped_list = [(
        el, data.count(el)) for el in data] 
    print([*set(grouped_list)])


def negative_comment_today(file_name):
    campaings = json.loads(open(file_name, "r").read())
    url = "https://smartsolutions.pythonanywhere.com/sentiment-graph/{}" # fetch from smart solutions 
    data = {}
    new_negative_comments = []
    old_negative_comments = []
    for cams in campaings:
        for adsets in cams['adsets']:
            for ads in adsets["ads"]:
                if len(ads["negative_comments"]) !=0:
                    for c in ads["negative_comments"]:
                        if Comment_made_today(c["created_time"]) and not c['is_hidden'] and not c['is_ignored']:
                            new_negative_comments.append(
                                {
                                    "comment": c['comment'], "adset_id": adsets['adset_id'], "comment_id": c['id'],
                                    "campaign_name": cams['campaign_name'], "url": url.format(adsets['adset_id'])                             
                                })
                        elif not c['is_hidden'] and not c['is_ignored']:
                            old_negative_comments.append(
                                {
                                    "comment": c['comment'], "adset_id": adsets['adset_id'], "comment_id": c['id'],
                                    "campaign_name": cams['campaign_name'], "url": url.format(adsets['adset_id'])
                                })
    data['new_negative_comments'] = new_negative_comments if len(new_negative_comments) != 0 else []
    data['old_negative_comments'] = old_negative_comments if len(old_negative_comments) != 0 else []
    return data


def total_comment_yesterday(file_name):
    url = "https://smartsolutions.pythonanywhere.com/sentiment-graph/{}" # fetch from smart solutions 
    campaings = json.loads(open(file_name, "r").read())
    store_data = []
    for cams in campaings:
        for adsets in cams['adsets']:
            for ads in adsets["ads"]:
                data = []
                if len(ads["positive_comments"]) !=0:
                    for c in ads["positive_comments"]:
                        if Comment_made_yesterday(c['created_time']):
                            data.append({
                            "comment": c['comment'], "adset_id": adsets['adset_id'], 
                            "adset_name": adsets['adset_name'],
                            "campaign_name": cams['campaign_name'], "ad_name": ads['ad_name'],
                            "url": url.format(adsets['adset_id']), "created_time": c['created_time']                           
                            })     
                    store_data += [{f"{ads['ad_name']}":data}]
    return store_data


def comment_count_in_ad():
    stored_data = total_comment_yesterday()
    data = []
    for sd in stored_data:
        for adname in sd:
            if len(sd[adname]) != 0:
                data.append(
                    {
                        "ad_name": adname, "adset_name": sd[adname][0]['adset_name'], 
                        "campaign_name": sd[adname][0]['campaign_name'], "count": len(sd[adname]), 
                        "url": sd[adname][0]['url']
                    }
                )
    return data 
            
    

if __name__ == "__main__":
    file_name = "JSON/negative_comments.json"
    # save_campaings(file_name) # saving active campaigns 
    # save_ads(file_name) # save ads from campaign
    save_comments(file_name)
    # active_campaigns()
    # save_ads()
    # save_negative_comments()