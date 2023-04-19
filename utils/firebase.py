"""
firebase.py

This module caches video information in Firebase using the user's id as the key.
Cached video entries include duration, title, channel name, category, and timestamp.
The timestamp acts as a TTL of 24 hours, and entries older than the TTL are updated by requesting
the video information from the YouTube API.
"""

# autopep8: off
# Necessary imports
import os
import sys
import json
from datetime import datetime, timedelta

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.credentials import *
from utils.youtube_utils import get_video_information
from utils.imports import *
# autopep8: on


def is_video_cached(video_id, data_from_cache):
    """
    Check if a video is cached in Firebase and not expired.

    Args:
        - video_id (str): The ID of the video to check.
        - data_from_cache (dict): The video data dictionary obtained from Firebase cache.

    Returns:
        - bool: True if the video is cached and not expired, False otherwise.
    """

    required_attributes = ['timestamp', 'duration',
                           'title', 'channel_name', 'category']
    if not data_from_cache or video_id not in data_from_cache:
        return False

    for attribute in required_attributes:
        if attribute not in data_from_cache[video_id]:
            return False

    timestamp = datetime.strptime(
        data_from_cache[video_id]['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
    return datetime.now() - timestamp < timedelta(days=1)


def get_uncached_video_ids(video_ids, data_from_cache):
    """
    Returns a list of uncached or expired video IDs.

    Args:
        - video_ids (list): A list of video IDs.
        - data_from_cache (dict): The video data dictionary obtained from Firebase cache.

    Returns:
        - uncached_video_ids (list): A list of uncached or expired video IDs.
    """

    uncached_video_ids = []
    for video_id in video_ids:
        if not is_video_cached(video_id, data_from_cache):
            uncached_video_ids.append(video_id)
    return uncached_video_ids


async def cache_video_data_async(user_email, video_id, video_data):
    """
    Caches video information in Firebase for a given video ID.

    Args:
        - user_email (str): The user's email address.
        - video_id (str): The ID of the video to cache.
        - video_data (dict): The video data dictionary to cache.
    """

    url = f'{FIREBASE_DB_URL}/{user_email}/{video_id}.json?auth={FIREBASE_API_KEY}'
    async with httpx.AsyncClient() as client:
        await client.put(url, json=video_data)


async def cache_request(youtube, video_ids, cache_function=cache_video_data_async):
    """
    Caches video information in Firebase for a given list of video IDs. 

    The function checks if the video IDs are cached in Firebase and not expired. If the video IDs 
    are not cached, the function requests the video information from the YouTube API, updates the 
    cache with the new video information, and returns the video information. 

    Args:
        - youtube (googleapiclient.discovery.Resource): A Youtube API client.
        - video_ids (list): A list of video IDs for which to retrieve information.

    Returns:
        - video_info (dict): A dictionary where the keys are the video IDs and the values are dictionaries with 
              information such as duration, title, channel name, and category.
    """

    user_email = USER_ID.replace('@', '-').replace('.', '-')
    video_info = {}

    # Check if the video_ids are in Firebase cache
    url = f'{FIREBASE_DB_URL}/{user_email}.json?auth={FIREBASE_API_KEY}'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    data_from_cache = response.json()

    if data_from_cache is None:
        data_from_cache = {}

    # Get uncached_video_ids
    uncached_video_ids = get_uncached_video_ids(video_ids, data_from_cache)

    # If there are uncached videos, request the video information from YouTube API
    if uncached_video_ids:
        uncached_video_data = get_video_information(
            youtube, uncached_video_ids)

        # Update the cache with the new video information
        async with httpx.AsyncClient() as client:
            tasks = []
            for video_id, data in uncached_video_data.items():
                data['duration'] = isodate.duration_isoformat(data['duration'])
                data['timestamp'] = datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S.%f")
                data['channel_name'] = data['channel_name']
                data['category'] = data.get('category', 'Unknown')
                tasks.append(cache_function(user_email, video_id, data))
            await asyncio.gather(*tasks)

    # Build video_info from cache data and newly fetched data
    for video_id in video_ids:
        if video_id in data_from_cache:
            try:
                video_info[video_id] = {
                    'duration': timedelta(seconds=isodate.parse_duration(data_from_cache[video_id]['duration']).total_seconds()),
                    'title': data_from_cache[video_id]['title'],
                    'channel_name': data_from_cache[video_id]['channel_name'],
                    'category': data_from_cache[video_id].get('category', 'Unknown')
                }
            except isodate.isoerror.ISO8601Error:
                pass
        elif video_id in uncached_video_data:
            video_info[video_id] = {
                'duration': timedelta(seconds=isodate.parse_duration(uncached_video_data[video_id]['duration']).total_seconds()),
                'title': uncached_video_data[video_id]['title'],
                'channel_name': uncached_video_data[video_id]['channel_name'],
                'category': uncached_video_data[video_id]['category']
            }

    return video_info
