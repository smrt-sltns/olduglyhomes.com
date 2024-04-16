from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Set up OAuth 2.0 credentials
flow = InstalledAppFlow.from_client_secrets_file(
    'sm_client.json',
    scopes=['https://www.googleapis.com/auth/youtube.readonly']
)
credentials = flow.run_local_server()

# Build a YouTube service object using the credentials
youtube = build('youtube', 'v3', credentials=credentials)

# Call the subscriptions.list method to retrieve a list of subscribers
subscribers_response = youtube.subscriptions().list(
    part='snippet',
    channelId='UCLuej1erRngQG0G5xSvYtCA',
    maxResults=50
).execute()

# Extract the list of subscribers
subscribers = subscribers_response.get('items', [])

# Print subscriber details
for subscriber in subscribers:
    print(f"Subscriber ID: {subscriber['snippet']['resourceId']['channelId']}")
    print(f"Subscriber Title: {subscriber['snippet']['title']}")
    print("---------------------------------------------------------")

#sm access token
access_token="ya29.a0Ad52N3-dzRg9RZYvFCDAUHwImnWNkgr0ahDmCdjvzUyLyMHM-74AeRTvW4CHm0kGmUPKvMsAnS4crswY02TI381BcJpU32T4qeD_5-xyxJxeddxONCtuFmfN5UhYrz8e54V18mjXKXgjY-JujHKWA8q0VkrYWhXE7XNxaCgYKAVkSARMSFQHGX2Mi29sESYwfHU1fSYPYPEkhAg0171"