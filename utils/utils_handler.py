# autopep8: off
import os
import sys
import json
import requests
from datetime import datetime, timedelta

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.firebase import is_valid_cache, cache_video_data
from utils.youtube_utils import get_video_duration, get_video_category
from utils.imports import *
from config.credentials import *
# autopep8: on

# should check if cached, if not request from youtube
def get_video_data_and_cache(video_id, video_data):
    try:
        if is_valid_cache(video_id):
            video_data = retrieve_cached_video_data(video_id)
        else:
            service = 'youtube'
            version = 'v3'
            youtube = googleapiclient.discovery.build(service, version, developerKey=YOUTUBE_API_KEY)
            video_data['duration'] = get_video_duration(youtube, video_id)
            video_data['category'] = get_video_category(youtube, video_id)
            cache_video_data(video_id, video_data, 24)
        return video_data
    except Exception as e:
        logging.error(f"Error when utility handler tried accessing video data: {e}")
        raise e
    

if __name__ == "__main__":
    video = get_video_data('iWz7ctlFuX0', {'duration': 'test', 'category': 'test'})
    print(video)