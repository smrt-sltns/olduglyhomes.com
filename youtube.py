from googleapiclient.discovery import build
import datetime

# YouTube API configuration
API_KEY = 'AIzaSyA8Vk-BGwwz8cV_yhE9R9LXk6eYthDvBzI'  # Replace with your actual API key
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def get_video_details(youtube, video_id):
    """
    Fetches the details of a YouTube video using its video ID.
    """
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()
    
    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]
    else:
        return None

def calculate_watch_time(video_statistics, average_watch_duration):
    """
    Calculate the total watch time for a video based on its view count and average watch duration.
    """
    view_count = int(video_statistics.get('viewCount', 0))
    total_watch_time = view_count * average_watch_duration
    return total_watch_time

def main():
    # Initialize the YouTube API client
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

    # List of video IDs to analyze
    video_ids = ['8Pvv9W9ix5Y', 'C0eXq7w5Cwc', '4QsNeBceD48']  # Replace with actual video IDs

    # Hypothetical average watch duration in seconds (you might need to adjust this value)
    average_watch_duration = 300  # 5 minutes

    total_hours_spent = 0

    # Fetch video details and calculate total watch time
    for video_id in video_ids:
        video_details = get_video_details(youtube, video_id)
        if video_details:
            statistics = video_details['statistics']
            watch_time = calculate_watch_time(statistics, average_watch_duration)
            total_hours_spent += watch_time / 3600  # Convert seconds to hours
            print(f"Video ID: {video_id} - Watch Time: {watch_time / 3600:.2f} hours")

    print(f"Total hours spent on all videos: {total_hours_spent:.2f} hours")

if __name__ == "__main__":
    main()
