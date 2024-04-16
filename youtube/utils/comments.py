from googleapiclient.discovery import build

def comments(video_id, api_key=None, client_id=None, client_secret=None, refresh_token=None):
    # Build a YouTube service object using the API key or OAuth credentials
    if api_key:
        youtube = build('youtube', 'v3', developerKey=api_key)
    else:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        # Set up OAuth flow for user authorization
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=['https://www.googleapis.com/auth/youtube.readonly']
        )

        # Fetch credentials
        credentials = Credentials(
            token=None,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token'
        )

        # Authorize the OAuth flow
        youtube = build('youtube', 'v3', credentials=credentials)

    # Call the commentThreads.list method to retrieve comment threads for the video
    comment_threads = []
    nextPageToken = None
    while True:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            pageToken=nextPageToken
        ).execute()

        for item in response['items']:
            comment_threads.append({
                'id': item['id'],
                'author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                'text': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                'published_at': item['snippet']['topLevelComment']['snippet']['publishedAt'],
                'replies': []
            })

            # Check if the comment thread has replies
            if 'replies' in item:
                for reply in item['replies']['comments']:
                    comment_threads[-1]['replies'].append({
                        'author': reply['snippet']['authorDisplayName'],
                        'text': reply['snippet']['textDisplay'],
                        'published_at': reply['snippet']['publishedAt']
                    })

        if 'nextPageToken' in response:
            nextPageToken = response['nextPageToken']
        else:
            break

    return comment_threads

if __name__ == "__main__":
    # Example usage
    video_id = 'pzPdl_HApa4'
    api_key = 'AIzaSyD5JKPlyhbGD21fycFDEjahkilTFpznLVM'
    comment_threads = comments(video_id, api_key=api_key)

    print(comment_threads)
    for comment_thread in comment_threads:
        print(f"Comment ID: {comment_thread['id']}")
        print(f"Author: {comment_thread['author']} ({comment_thread['published_at']})")
        print(f"Text: {comment_thread['text']}")
        print("Replies:")
        for reply in comment_thread['replies']:
            print(f"\t{reply['author']} ({reply['published_at']}): {reply['text']}")
        print("-------------------------------------")