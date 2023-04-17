import json
import isodate
import requests
from datetime import datetime, timedelta

from config import config
from youtube_utils import get_video_information

firebase_api_key = config.FIREBASE_API_KEY
firebase_db_url = config.FIREBASE_DB_URL
user_id = config.USER_ID

def cache_request(youtube, video_ids):
    user_email = user_id.replace('@', '-').replace('.', '-')
    video_info = {}
    for video_id in video_ids:
        # Check if the video_id is in Firebase cache
        url = f'{firebase_db_url}/{user_email}/{video_id}.json?auth={firebase_api_key}'
        response = requests.get(url)
        video_data_from_cache = response.json()

        # Check if the timestamp is older than 24 hours
        should_update = True
        if video_data_from_cache and 'timestamp' in video_data_from_cache:
            timestamp = datetime.strptime(video_data_from_cache['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
            if datetime.now() - timestamp < timedelta(days=1):
                should_update = False

        if not should_update:
            video_info[video_id] = {
                'duration': isodate.parse_duration(video_data_from_cache['duration']),
                'title': video_data_from_cache['title']
            }
        else:
            # If not in cache or TTL is older than 24 hours,
            # request the video information from YouTube API
            video_data = get_video_information(youtube, [video_id])
            video_info.update(video_data)

            if video_id in video_data:
                # Convert duration to ISO 8601 format before storing in Firebase
                video_data[video_id]['duration'] = isodate.duration_isoformat(video_data[video_id]['duration'])

                # Add a timestamp to the video data
                video_data[video_id]['timestamp'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

                # Store the video data in Firebase cache
                response = requests.put(url, json.dumps(video_data[video_id]))

                # Print status code and response content if the status code is not 200
                if response.status_code != 200:
                    print(f"Uploading video_id {video_id} to Firebase:")
                    print(f"Status code: {response.status_code}")
                    print(f"Response content: {response.content}")

    return video_info