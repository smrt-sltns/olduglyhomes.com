from youtube.Analytics.authorize import authenticate_youtube
import datetime 
from youtube.Analytics.creadFile import CredFile
from youtube.Analytics.tokenFile import TokenFile


youtube_analytics = authenticate_youtube(cred_file=CredFile.CREAD_SAP, token_file=TokenFile.TOKEN_SAP)

def get_video_average_watch_duration(youtube_analytics, video_id):
    """
    Fetches the average watch duration for a specific video using YouTube Analytics API.
    """
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=30)
    response = youtube_analytics.reports().query(
        ids="channel==MINE",
        startDate=start_date.strftime('%Y-%m-%d'),
        endDate=end_date.strftime('%Y-%m-%d'),
        metrics="views,comments,likes,dislikes,estimatedMinutesWatched,averageViewDuration",
        dimensions="video",
        filters=f"video=={video_id}"
    ).execute()
    import json 
    json_object = json.dumps(response, indent=4)
    json_file = open("sap_video.json", "w")
    json_file.write(json_object)
    json_file.close()
    if 'rows' in response:
        avg_watch_duration = response['rows'][0][-2]
        return avg_watch_duration
    else:
        return None