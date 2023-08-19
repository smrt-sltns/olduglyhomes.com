import requests



## FOR AD ACCOUNTS
# api keys of graph api APP
api_key = "515142624070049"
api_secret = "3e98aef4fd094f0480e7aef277548bda"

## FOR AD ACCOUNTS
ACCESS_TOKEN = ""
LONGLIVED_ACCESS_TOKEN = ""

## FOR USER ACCESS TOKEN
USER_ACCESS_TOKEN = ""
USER_LONGLIVED_ACCESS_TOKEN = ""

def get_long_lived_access_token():
    url = u"https://graph.facebook.com/v16.0/oauth/access_token?grant_type=fb_exchange_token&client_id={}&client_secret={}&fb_exchange_token={}".format(api_key, api_secret, ACCESS_TOKEN)
    access = requests.get(url)
    print(access.content)


if __name__ == "__main__":
    get_long_lived_access_token()

# get_long_lived_access_token()