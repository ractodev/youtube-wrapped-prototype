import googleapiclient.errors
from datetime import timedelta
import isodate

# Fetch video information such as title and duration
def get_video_information(youtube, video_ids):
    video_info = {}
    try:
        response = youtube.videos().list(
            part="snippet,contentDetails",
            id=",".join(video_ids),
        ).execute()
        
        for item in response["items"]:
            video_id = item["id"]
            video_info[video_id] = {
                "title": item["snippet"]["title"],
                "duration": isodate.parse_duration(item["contentDetails"]["duration"]),
            }
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")
    
    return video_info

# Retrieve user's watch history
def get_watch_history(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        watch_history = [line.strip() for line in file.readlines()]
    return watch_history