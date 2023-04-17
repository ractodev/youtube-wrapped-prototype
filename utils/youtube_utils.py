"""
youtube_utils.py:

This module provides helper functions to interact with the YouTube Data API v3.

Functions:
    - get_video_information(): Fetches video information such as title and duration for a list of video IDs using the YouTube API.
    - get_watch_history(): Retrieves the user's watch history from a file path and returns it as a list.
"""

# Necessary imports
import os
import sys

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local modules
from utils.imports import *


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
                "channel_name": item["snippet"]["channelTitle"],
            }
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")
    
    return video_info

def get_watch_history(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        watch_history = [line.strip() for line in file.readlines()]
    return watch_history