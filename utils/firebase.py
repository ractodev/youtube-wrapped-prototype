"""
firebase.py

This module caches video information in Firebase using the user's id as the key.
Cached video entries include duration, title, and timestamp. The timestamp acts
as a TTL of 24 hours, and entries older than the TTL are updated by requesting
the video information from the YouTube API.

Functions:
    - is_video_cached(): Checks if a video is cached in Firebase and not expired.
    - get_uncached_video_ids(): Returns a list of uncached or expired video IDs.
    - cache_video_data(): Caches video information in Firebase for a given video ID.
    - cache_request(): Caches video information in Firebase if not already cached or expired.
"""


# Necessary imports
import os
import sys
import json
from datetime import datetime, timedelta

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local modules
from utils.imports import *
from utils.youtube_utils import get_video_information

# Credentials
from config.credentials import *


def is_video_cached(video_id, data_from_cache):
    if not data_from_cache or video_id not in data_from_cache or 'timestamp' not in data_from_cache[video_id]:
        return False

    timestamp = datetime.strptime(data_from_cache[video_id]['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
    return datetime.now() - timestamp < timedelta(days=1)

def get_uncached_video_ids(video_ids, data_from_cache):
    uncached_video_ids = []
    for video_id in video_ids:
        if not is_video_cached(video_id, data_from_cache):
            uncached_video_ids.append(video_id)
    return uncached_video_ids

def cache_video_data(user_email, video_id, video_data):
    url = f'{FIREBASE_DB_URL}/{user_email}/{video_id}.json?auth={FIREBASE_API_KEY}'
    response = requests.put(url, json.dumps(video_data))

def cache_request(youtube, video_ids):
    user_email = USER_ID.replace('@', '-').replace('.', '-')
    video_info = {}

    # Check if the video_ids are in Firebase cache
    url = f'{FIREBASE_DB_URL}/{user_email}.json?auth={FIREBASE_API_KEY}'
    response = requests.get(url)
    data_from_cache = response.json()

    if data_from_cache is None:
        data_from_cache = {}

    uncached_video_ids = get_uncached_video_ids(video_ids, data_from_cache)

    # If there are uncached videos, request the video information from YouTube API
    if uncached_video_ids:
        video_data = get_video_information(youtube, uncached_video_ids)

        # Update the cache with the new video information
        for video_id, data in video_data.items():
            # Convert duration to ISO 8601 format before storing in Firebase
            data['duration'] = isodate.duration_isoformat(data['duration'])

            # Add a timestamp to the video data
            data['timestamp'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

            cache_video_data(user_email, video_id, data)

    # Build video_info from cache data and newly fetched data
    for video_id in video_ids:
        if video_id in data_from_cache:
            try:
                video_info[video_id] = {
                    'duration': timedelta(seconds=isodate.parse_duration(data_from_cache[video_id]['duration']).total_seconds()),
                    'title': data_from_cache[video_id]['title']
                }
            except isodate.isoerror.ISO8601Error:
                pass
        elif video_id in video_data:
            video_info[video_id] = {
                'duration': timedelta(seconds=isodate.parse_duration(video_data[video_id]['duration']).total_seconds()),
                'title': video_data[video_id]['title']
            }

    return video_info
