import requests 
import urllib.request 
import json 

token = ""
def handle_api_response():
    url = f"https://graph.facebook.com/v16.0/me?&access_token={token}"
    print(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print("Data:", data)
    except requests.exceptions.RequestException as e:
        print("Error making the request:", e)
        if response.status_code == 400:
            # print(400)
            try:
                error_data = response.json()
                error_message = error_data.get('error', 'Unknown Error')
                print("API Error:", error_message)
            except ValueError:
                print("API Error - Unable to parse error response:", response.text)



if __name__ == "__main__":
    handle_api_response()