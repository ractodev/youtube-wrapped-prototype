"""
watch_time.py:

This file calculates total watch time and most watched videos on YouTube using Google APIs.
Watch history is extracted from a Google Takeout file, video IDs are cached, and video info
is requested from the YouTube API. Results are cached in Firebase and printed to console.
"""

# autopep8: off
# Necessary imports
import os
import sys

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pre_processing import parse_watch_history
from src.analyser import get_total_watch_time, get_toplist
from config.credentials import * 
from utils.utils_handler import get_video_data_and_cache
from utils.imports import *
# autopep8: on

def main():
    print("Processing watch history...")
    watch_history = parse_watch_history()
    print("Lets retrieve some data...")

    full_video_data = {}
    with tqdm(total=len(watch_history), unit=' videos', desc="Retrieving video data") as pbar:
        for video_id, video_data in watch_history.items():
            if video_data:
                full_video_data[video_id] = get_video_data_and_cache(video_id, video_data)
            pbar.update(1)

    total_watch_time = get_total_watch_time(full_video_data)
    top_videos = get_toplist(full_video_data, 'title', 10)
    top_channels = get_toplist(full_video_data, 'channel', 5)
    top_categories = get_toplist(full_video_data, 'category', 5)

    print(f"\nTotal watch time: {total_watch_time} minutes watched.")
    print(f"Total number of videos watched: {len(full_video_data)}\n")

    print("Top 10 videos:")
    for i, video in enumerate(top_videos):
        print(f"{i+1}. {video[0]} ({video[1]} views)")

    print("\nTop 5 channels:")
    for i, channel in enumerate(top_channels):
        print(f"{i+1}. {channel[0]} ({channel[1]} views)")

    print("\nTop 5 categories:")
    for i, category in enumerate(top_categories):
        print(f"{i+1}. {category[0]} ({category[1]} views)")
    

if __name__ == "__main__":
    main()
