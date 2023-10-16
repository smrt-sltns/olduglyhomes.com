from access_token import LONGLIVED_ACCESS_TOKEN
import json 
import urllib.request
from textblob import TextBlob
from datetime import datetime






#Save all active campaigns 
def save_campaings(file_name="JSON/active_campaigns.json",account_id="act_296865963", token=LONGLIVED_ACCESS_TOKEN):
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
    with open(file_name, 'w') as json_file:
        json_objects = json.dumps(data, indent=4)
        json_file.write(json_objects)
    print(file_name, "Saved!")


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
                                    "eff":eff, "negative_comments":[], "positive_comments":[] })
                c['adsets'].append({"adset_name": adset_name, "adset_id": adset_id, "ads": ads})
        data.append(c)
    with open(file_name, 'w') as json_file:
        json_objects = json.dumps(data, indent=4)
        json_file.write(json_objects)
    print("ads saved")


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



def save_comments(file_name, token):
    campaigns = json.loads(open(file_name, "r").read())    
    for camps in campaigns:
        for adset in camps['adsets']:
            for ad in adset['ads']:
                if ad['status'] == "ACTIVE":
                    eff = ad['eff']
                    negative_comments_list, positive_comments_list = get_comments(eff, token=token)
                    ad['negative_comments'] = negative_comments_list
                    ad['positive_comments'] = positive_comments_list
    with open(file_name, 'w') as json_file: 
        json_object = json.dumps(campaigns, indent=4)
        json_file.write(json_object)
    print("Active campaign json file is updated with negative comments!")


def email_to_file_name(email):
    break_at = str(email).split("@")[0]
    if "." in break_at:
        join_ = "_".join(break_at.split("."))
        return  join_
    else:
        return  break_at


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
                                    "comment": c['comment'], "comment_id": c['id'], #comment
                                    "created_time":c['created_time'], #comment created time 
                                    "ad_id": ads['ad_id'], "ad_name":ads["ad_name"], #ad 
                                    "adset_id": adsets['adset_id'], "adset_name": adsets['adset_name'], #adset
                                    "campaign_id":cams['campaign_id'], "campaign_name": cams['campaign_name'], #campaign
                                    "url": url.format(adsets['adset_id']) #url
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
                            # sending comment and id but not saving in the db 
                            # 
                            "comment": c['comment'], "comment_id": c['id'],
                            "ad_name": ads['ad_name'], "ad_id": ads['ad_id'],
                            "adset_id": adsets['adset_id'], "adset_name": adsets['adset_name'],
                            "campaign_name": cams['campaign_name'],"campaign_id": cams['campaign_id'],
                            "url": url.format(adsets['adset_id']), "created_time": c['created_time']                           
                            })     
                    store_data += [{f"{ads['ad_name']}":data}]
    return store_data


def comment_count_in_ad(file_name):
    stored_data = total_comment_yesterday(file_name)
    data = []
    for sd in stored_data:
        for adname in sd:
            if len(sd[adname]) != 0:
                data.append(
                    {
                        "ad_name": adname, "ad_id":sd[adname][0]['ad_id'],
                        "adset_name": sd[adname][0]['adset_name'], "adset_id": sd[adname][0]['adset_id'],
                        "campaign_name": sd[adname][0]['campaign_name'], "campaign_id": sd[adname][0]['campaign_id'],
                        "count": len(sd[adname]), "created_time": sd[adname][0]['created_time'],
                        "url": sd[adname][0]['url']
                    }
                )
    return data 
            
    

if __name__ == "__main__":
    file_name = "JSON/negative_comments.json"
    save_comments(file_name)