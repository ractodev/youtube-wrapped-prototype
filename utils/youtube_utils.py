"""
youtube_utils.py:

This module provides helper functions to interact with the YouTube Data API v3.
"""

# autopep8: off
# Necessary imports
import os
import sys 

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.imports import *
from config.credentials import * # REMOVE
# autopep8: on

def get_video_duration(youtube, video_id):
    try:
        response = youtube.videos().list(part='contentDetails', id=video_id).execute()
        duration = response['items'][0]['contentDetails']['duration']
        return duration
    except Exception as e:
        logging.error(f"Error fetching duration for video ID {video_id}: {e}")

def get_video_category(youtube, video_id):
    try:
        response = youtube.videos().list(part='snippet', id=video_id).execute()
        category_id = response['items'][0]['snippet']['categoryId']
        category_response = youtube.videoCategories().list(part='snippet', id=category_id).execute()
        category_name = category_response['items'][0]['snippet']['title']
        return category_name
    except Exception as e:
        logging.error(f"Error fetching category for video ID {video_id}: {e}")
