# firebase.py

# autopep8: off
import os
import sys
import json
import requests
from datetime import datetime, timedelta

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.imports import *
from config.credentials import *
# autopep8: on


def cache_video_data(video_id, video_data, ttl_hours):
    url = f'{FIREBASE_DB_URL}/{USER_ID}/{video_id}.json?auth={FIREBASE_API_KEY}'
    expiration_time = datetime.now() + timedelta(hours=ttl_hours)
    timestamp = expiration_time.timestamp()
    video_data['ttl'] = timestamp
    try:
        response = requests.put(url, json=video_data)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"An error occurred while making the request with error code: {response.status_code}. Reason: {response.reason}.")
        raise e


def retrieve_cached_video_data(video_id):
    url = f'{FIREBASE_DB_URL}/{USER_ID}/{video_id}.json?auth={FIREBASE_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data:
            return data
        else:
            return False
    except requests.RequestException as e:
        logging.error(f"An error occurred while checking if video {video_id} is cached: {e}")
        raise e


def is_valid_cache(video_id):
    response = retrieve_cached_video_data(video_id)
    required_parameters = ['video_title', 'channel_name', 'duration', 'category', 'video_url', 'ttl']
    if response and all(param in response and response[param] is not None for param in required_parameters):
        ttl_datetime = datetime.fromtimestamp(response['ttl'])
        current_datetime = datetime.now()
        return current_datetime < ttl_datetime
    else:
        return False
