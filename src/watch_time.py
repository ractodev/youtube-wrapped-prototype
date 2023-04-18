"""
watch_time.py:

This file calculates total watch time and most watched videos on YouTube using Google APIs. 
Watch history is extracted from a Google Takeout file, video IDs are cached, and video info 
is requested from the YouTube API. Results are cached in Firebase and printed to console.

Functions:
    - authenticate(): Builds a Youtube API client with the provided API key.
    - retrieve_watch_history(): Retrieves the user's watch history from a file and returns it as a list.
    - retrieve_video_info(): Retrieves video information such as title and duration for a list of video IDs using the YouTube API.
    - calculate_stats(): Calculates the user's total watch time and most watched videos based on their watch history and video information.
    - display_results(): Displays the user's total watch time and most watched videos on console.
    - display_top_items(): Helper function to display top x items of a certain category, such as videos or channels, along with their respective counts.
    - main(): Orchestrates the program by calling the necessary functions to calculate the user's watch time and most watched videos.

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
    return googleapiclient.discovery.build(service, version, developerKey=api_key)


def retrieve_watch_history():
    extracted_video_ids_path = '../data/extracted_video_ids.txt'
    if not os.path.exists(extracted_video_ids_path):
        preprocess_watch_history()

    return get_watch_history(extracted_video_ids_path)


def retrieve_video_info(youtube, watch_history):
    video_info = {}
    batch_size = 50
    with tqdm(total=len(watch_history), unit='videos', desc="Processing watch history") as pbar:
        for i in range(0, len(watch_history), batch_size):
            video_ids_batch = watch_history[i:i + batch_size]
            video_info_batch = cache_request(youtube, video_ids_batch)
            video_info.update(video_info_batch)
            pbar.update(len(video_ids_batch))

    return video_info


def calculate_stats(watch_history, video_info):
    total_watch_time = timedelta()
    video_count = collections.defaultdict(int)
    channel_count = collections.defaultdict(int)
    category_count = collections.defaultdict(int)

    for video_id in watch_history:
        if video_id in video_info:
            duration = video_info[video_id]['duration']
            total_watch_time += duration
            video_count[video_id] += 1

            channel_name = video_info[video_id]['channel_name']
            channel_count[channel_name] += 1

            category_name = video_info[video_id]['category']
            category_count[category_name] += 1

    return total_watch_time, video_count, channel_count, category_count


def display_results(watch_history, total_watch_time, video_count, channel_count, category_count, video_info):
    print(f"\nTotal watch time: {total_watch_time.total_seconds() / 60:.1f} minutes watched")
    print(f"Total number of videos watched: {len(watch_history)}")

    print("\nTop 10 videos:")
    display_top_items(video_count, video_info, "views", 10)

    print("\nTop 5 channels:")
    display_top_items(channel_count, None, "views", 5)

    print("\nTop 5 categories:")
    display_top_items(category_count, None, "views", 5)


def display_top_items(item_count, item_info, item_label, x):
    top_items = sorted(item_count.items(), key=lambda x: x[1], reverse=True)[:x]
    for i, (item_id, count) in enumerate(top_items, start=1):
        if item_info and item_id in item_info:
            item_name = item_info[item_id]['title'] if item_label == "views" else item_info[item_id]
        else:
            item_name = item_id
        print(f"{i}. {item_name} ({count} {item_label})")

def main():
    youtube = authenticate(YOUTUBE_API_KEY)
    watch_history = retrieve_watch_history()
    video_info = retrieve_video_info(youtube, watch_history)
    total_watch_time, video_count, channel_count, category_count = calculate_stats(watch_history, video_info)
    display_results(watch_history, total_watch_time, video_count, channel_count, category_count, video_info)

if __name__ == "__main__":
    main()
