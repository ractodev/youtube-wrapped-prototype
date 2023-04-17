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

# Necessary imports
import os
import sys

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local modules
from utils.imports import *
from utils.firebase import cache_request
from utils.youtube_utils import get_video_information, get_watch_history
from pre_processing import preprocess_watch_history

# Credentials
from config.credentials import *


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
    video_count = collections.defaultdict(int)

    # Get video information from cache or Youtube API
    video_info = {}
    batch_size = 50
    num_batches = (len(watch_history) + batch_size - 1) // batch_size
    with tqdm(total=len(watch_history), unit='videos', desc="Processing watch history") as pbar:
        for i in range(0, len(watch_history), batch_size):
            video_ids_batch = watch_history[i:i + batch_size]
            video_info_batch = cache_request(youtube, video_ids_batch)
            video_info.update(video_info_batch)
            pbar.update(len(video_ids_batch))

    # Calculate total watch time
    for video_id in watch_history:
        if video_id in video_info:
            duration = video_info[video_id]['duration']
            total_watch_time += duration
            video_count[video_id] += 1

    print(f"\nTotal watch time: {total_watch_time.total_seconds() / 60:.1f} minutes watched")
    print(f"Total number of videos watched: {len(watch_history)}")

    # Display the top 10 most-watched videos
    print("\nTop 10 videos:")
    top_videos = sorted(video_count.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (video_id, count) in enumerate(top_videos, start=1):
        if video_id in video_info:
            title = video_info[video_id]['title']
            print(f"{i}. {title} ({count} views)")

if __name__ == "__main__":
    main()
