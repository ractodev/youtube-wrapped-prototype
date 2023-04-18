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
from config.credentials import * 
from pre_processing import preprocess_watch_history
from utils.youtube_utils import get_video_information, get_watch_history
from utils.firebase import cache_request
from utils.imports import *
# autopep8: on


# Build Youtube API client
def authenticate(api_key):
    """
    Builds a Youtube API client with the provided API key.

    Args:
        - api_key (str): API key for the YouTube API.

    Returns:
        - The built YouTube API client.
    """

    service = 'youtube'
    version = 'v3'
    return googleapiclient.discovery.build(service, version, developerKey=api_key)


def retrieve_watch_history():
    """
    Retrieves the user's watch history from a file and returns it as a list.

    Args:
        - None

    Returns:
        - List of video IDs in the user's watch history.
    """

    extracted_video_ids_path = '../data/extracted_video_ids.txt'
    preprocess_watch_history()

    return get_watch_history(extracted_video_ids_path)


def retrieve_video_info(youtube, watch_history):
    """
    Retrieves video information such as title and duration for a list of video IDs using the YouTube API.

    Args:
        - youtube: The YouTube API client.
        - watch_history (list): List of video IDs to retrieve information for.

    Returns:
        - Dictionary with video information, where the keys are video IDs.
    """

    video_info = {}
    batch_size = 50
    with tqdm(total=len(watch_history), unit='videos', desc="Processing watch history") as pbar:
        for i in range(0, len(watch_history), batch_size):
            video_ids_batch = watch_history[i:i + batch_size]
            video_info_batch = asyncio.run(cache_request(youtube, video_ids_batch))
            video_info.update(video_info_batch)
            pbar.update(len(video_ids_batch))

    return video_info


def calculate_stats(watch_history, video_info):
    """
    Calculates the user's total watch time and most watched videos based on their watch history and video information.

    Args:
        - watch_history (list): List of video IDs in the user's watch history.
        - video_info (dict): Dictionary with video information, where the keys are video IDs.

    Returns:
        - A tuple with the total watch time as a timedelta object, a dictionary with video IDs as keys and view counts as values,
        - a dictionary with channel names as keys and view counts as values, and a dictionary with category names as keys and view counts as values.
    """

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
    """
    Displays the user's total watch time and most watched videos on console.

    Args:
        - watch_history (list): List of video IDs extracted from Google Takeout watch history file.
        - total_watch_time (datetime.timedelta): Total time watched by the user.
        - video_count (collections.defaultdict): Number of times each video was watched.
        - channel_count (collections.defaultdict): Number of times each channel was watched.
        - category_count (collections.defaultdict): Number of times each category was watched.
        - video_info (dict): Information for each video in the user's watch history, including title, duration, and channel name.

    Returns:
        - None
    """

    print(
        f"\nTotal watch time: {total_watch_time.total_seconds() / 60:.1f} minutes watched")
    print(f"Total number of videos watched: {len(watch_history)}")

    print("\nTop 10 videos:")
    display_top_items(video_count, video_info, "views", 10)

    print("\nTop 5 channels:")
    display_top_items(channel_count, None, "views", 5)

    print("\nTop 5 categories:")
    display_top_items(category_count, None, "views", 5)


def display_top_items(item_count, item_info, item_label, x):
    """
    Display top x items of a certain category along with their respective counts.

    Args:
        - item_count (dict): A dictionary containing item IDs as keys and their count as values.
        - item_info (dict): A dictionary containing item IDs as keys and their information as values. If None, the item ID is displayed as the name.
        - item_label (str): A label for the item count, e.g. 'views'.
        - x (int): The number of top items to display.

    Returns:
        - None
    """

    top_items = sorted(item_count.items(),
                       key=lambda x: x[1], reverse=True)[:x]
    for i, (item_id, count) in enumerate(top_items, start=1):
        if item_info and item_id in item_info:
            item_name = item_info[item_id]['title'] if item_label == "views" else item_info[item_id]
        else:
            item_name = item_id
        print(f"{i}. {item_name} ({count} {item_label})")


def main():
    """
    Orchestrates the program by calling the necessary functions to calculate the user's watch time and most watched videos.

    Args:
        - None

    Returns:
        - None
    """

    youtube = authenticate(YOUTUBE_API_KEY)
    watch_history = retrieve_watch_history()
    video_info = retrieve_video_info(youtube, watch_history)
    total_watch_time, video_count, channel_count, category_count = calculate_stats(
        watch_history, video_info)
    display_results(watch_history, total_watch_time, video_count,
                    channel_count, category_count, video_info)


if __name__ == "__main__":
    main()
