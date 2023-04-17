import json
import isodate
import requests

from config import config
from youtube_utils import get_video_information

firebase_api_key = config.FIREBASE_API_KEY
firebase_db_url = config.FIREBASE_DB_URL

def cache_request(youtube, video_ids):
    video_info = {}
    for video_id in video_ids:
        # Check if the video_id is in Firebase cache
        url = f'{firebase_db_url}/mydata/{video_id}.json?auth={firebase_api_key}'
        response = requests.get(url)
        video_data_from_cache = response.json()
        
        if video_data_from_cache and 'duration' in video_data_from_cache:
            video_info[video_id] = {
                'duration': isodate.parse_duration(video_data_from_cache['duration']),
                'title': video_data_from_cache['title']
            }
        else:
            # If not in cache, request the video information from YouTube API
            video_data = get_video_information(youtube, [video_id])

            if video_id in video_data:
                video_info.update(video_data)

                # Convert duration to ISO 8601 format before storing in Firebase
                video_data[video_id]['duration'] = isodate.duration_isoformat(video_data[video_id]['duration'])

                # Store the video data in Firebase cache
                response = requests.put(url, json.dumps(video_data[video_id]))

                # Print status code and response content if the status code is not 200
                if response.status_code != 200:
                    print(f"Uploading video_id {video_id} to Firebase:")
                    print(f"Status code: {response.status_code}")
                    print(f"Response content: {response.content}")
            #else:
            #    print(f"Video ID {video_id} not found in the YouTube API response.")

    return video_info

