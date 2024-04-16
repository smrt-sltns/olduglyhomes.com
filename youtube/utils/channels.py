from googleapiclient.discovery import build

# Your API key obtained from Google Cloud Console
# api_key = "AIzaSyBCeYPeprlUnwtuXQ81hrhzy2G2Gwsp9bE" #the real ustad 
# api_key = "AIzaSyD5JKPlyhbGD21fycFDEjahkilTFpznLVM" # soft marketing 
# # Your YouTube username
# youtube_id = "UC8D8LXvvSkJajP7WNOwMtTA" # the real ustad 
# youtube_id = "UCLuej1erRngQG0G5xSvYtCA"

def videos(api_key, channel_id):
    video_data = []
    channel_data = []
    # Build a YouTube service object using the API key
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Call the channels.list method to retrieve the channel ID
    channels_response = youtube.channels().list(
        part='id,snippet,statistics',
        id=channel_id,
        maxResults=100
    ).execute()
    

    # Check if the response contains any items
    if 'items' in channels_response and len(channels_response['items']) > 0:
        # Extract channel details
        channel = channels_response['items'][0]
        channel_id = channel['id']
        channel_username = channel['snippet']['title']
        channel_subscribers = channel['statistics']['subscriberCount']

        channel_data =[channel_id, channel_username, channel_subscribers]
        # # Print channel details
        # print(f"Channel ID: {channel_id}")
        # print(f"Username: {channel_username}")
        # print(f"Subscribers: {channel_subscribers}")
        # print("---------------------------------------------------------")

        # Call the playlistItems.list method to retrieve the uploads playlist ID
        uploads_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        # Extract the uploads playlist ID
        uploads_playlist_id = uploads_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Call the playlistItems.list method to retrieve the videos in the uploads playlist
        playlist_items_response = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=50  # Maximum number of videos to retrieve per request
        ).execute()

        # Extract the video IDs
        video_ids = [item['contentDetails']['videoId'] for item in playlist_items_response['items']]

        # Call the videos.list method to retrieve details for each video
        videos_response = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        ).execute()

        # Extract the list of videos
        videos = videos_response['items']

        # Print video details
        for video in videos:
            video_id = video['id']
            video_title = video['snippet']['title']
            video_published_at = video['snippet']['publishedAt']
            video_view_count = video['statistics'].get('viewCount', 0)
            video_comment_count = video['statistics'].get('commentCount', 0)
            video_like_count = video['statistics'].get('likeCount', 0)
            video_dislike_count = video['statistics'].get('dislikeCount', 0)

            # print(f"Video ID: {video_id}")
            # print(f"Title: {video_title}")
            # print(f"Published At: {video_published_at}")
            # print(f"View Count: {video_view_count}")
            # print(f"Comment Count: {video_comment_count}")
            # print(f"Like Count: {video_like_count}")
            # print(f"Dislike Count: {video_dislike_count}")
            # print("---------------------------------------------------------")
            row = [video_id, video_title, video_view_count,
                   video_like_count, video_dislike_count, 
                   video_comment_count, video_published_at]
            video_data.append(row)
    else:
        print("No channel found.")
    return channel_data, video_data