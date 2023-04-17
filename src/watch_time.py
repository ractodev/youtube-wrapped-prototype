"""
watch_time.py:

This file calculates total watch time and most watched videos on YouTube using Google APIs. 
Watch history is extracted from a Google Takeout file, video IDs are cached, and video info 
is requested from the YouTube API. Results are cached in Firebase and printed to console.

Functions:
    - authenticate(api_key): Builds a Youtube API client with the provided API key.
    - main(): Orchestrates the program by calling the necessary functions to calculate the user's
              watch time and most watched videos.
"""

import os
import sys
import time
from collections import Counter
from datetime import timedelta

import googleapiclient.discovery
import isodate
from bs4 import BeautifulSoup
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.credentials import *
from utils.firebase import cache_request
from src.pre_processing import preprocess_watch_history
from utils.youtube_utils import get_video_information, get_watch_history

# Build Youtube API client
def authenticate(api_key):
    service = 'youtube'
    version = 'v3'
    return googleapiclient.discovery.build(service, version, developerKey = api_key)
    
def main():
    extracted_video_ids_path = '../data/extracted_video_ids.txt'
    if not os.path.exists(extracted_video_ids_path):
        preprocess_watch_history()

    print("Authenticating to the Youtube API...")
    youtube = authenticate(YOUTUBE_API_KEY)
    print("Retrieving user's watch history...")
    watch_history = get_watch_history(extracted_video_ids_path)

    total_watch_time = timedelta()
    video_durations = {}
    most_watched = Counter(watch_history).most_common(10)

    # Generate progress bar for video information processing
    video_info = {}
    num_batches = (len(watch_history) + 49) // 50  # Calculate the number of batches, rounding up
    with tqdm(total=len(watch_history), unit='videos', desc="Processing watch history") as pbar:
        for i in range(0, len(watch_history), 50):
            video_ids = watch_history[i:i + 50]
            video_info_batch = cache_request(youtube, video_ids)
            video_durations.update({video_id: info['duration'] for video_id, info in video_info_batch.items()})
            video_info.update(video_info_batch)

            # Update the progress bar with the number of video IDs processed in the current batch
            pbar.update(len(video_ids))
    
    print("Top 10 most watched youtube videos:")
    for video_id, count in most_watched:
        title = video_info[video_id]['title']
        print(f"\t *{title} - Watched {count} times.")

    for video_id, count in most_watched:
        duration = video_durations.get(video_id, timedelta())
        total_watch_time += duration * count

    print(f"\nTotal time spent watching YouTube videos: {total_watch_time}")

if __name__ == "__main__":
    main()