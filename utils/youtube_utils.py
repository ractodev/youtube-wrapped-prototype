"""
youtube_utils.py:

This module provides helper functions to interact with the YouTube Data API v3.

Functions:
    - get_video_information(youtube, video_ids): Fetches video information such as title, duration, and category 
      for a list of video IDs using the YouTube API. Returns a dictionary of video IDs and their corresponding information.
    - get_watch_history(file_path): Retrieves the user's watch history from a file path and returns it as a list.
    - get_category_names(youtube, video_info): Returns a dictionary of category IDs and their corresponding 
      names based on a dictionary of video information.
    - get_video_details(youtube, video_ids): Helper function for `get_video_information()` that retrieves video details 
      such as title, duration, channel name, and category ID for a list of video IDs using the YouTube API. 
      Returns a dictionary of video IDs and their corresponding details.
"""

# Necessary imports
import os
import sys

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local modules
from utils.imports import *


def get_video_information(youtube, video_ids):
    video_info = get_video_details(youtube, video_ids)
    category_names = get_category_names(youtube, video_info)
    
    for video_id, info in video_info.items():
        category_id = info["category_id"]
        info["category"] = category_names.get(category_id, f"Unknown Category ({category_id})")

    return video_info

def get_video_details(youtube, video_ids):
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
                "channel_name": item["snippet"]["channelTitle"],
                "category_id": item["snippet"]["categoryId"]
            }
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")

    return video_info

def get_category_names(youtube, video_info):
    category_ids = {info["category_id"] for info in video_info.values()}
    category_names = {}

    try:
        category_response = youtube.videoCategories().list(
            part="snippet",
            id=",".join(category_ids),
        ).execute()

        for item in category_response["items"]:
            category_id = item["id"]
            category_names[category_id] = item["snippet"]["title"]
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")

    return category_names



def get_watch_history(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        watch_history = [line.strip() for line in file.readlines()]
    return watch_history