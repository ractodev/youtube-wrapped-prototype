import googleapiclient.discovery
from collections import Counter
from datetime import timedelta
from bs4 import BeautifulSoup
from tqdm import tqdm
import isodate
import time
import os

from pre_processing import preprocess_watch_history
from config import config

# Build Youtube API client
def authenticate(api_key):
    service = 'youtube'
    version = 'v3'
    return googleapiclient.discovery.build(service, version, developerKey = api_key)

# Retrieve user's watch history
def get_watch_history(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        watch_history = [line.strip() for line in file.readlines()]
    return watch_history

# Fetch video information, such as duration and title
def get_video_information(youtube, video_ids):
    request = youtube.videos().list(
        part = 'contentDetails,snippet',
        id = ','.join(video_ids)
    ).execute()
    return {
        item['id']: {
            'duration': isodate.parse_duration(item['contentDetails']['duration']),
            'title': item['snippet']['title']
        } for item in request['items']
    }
    
def main():
    extracted_video_ids_path = 'history/extracted_video_ids.txt'
    if not os.path.exists(extracted_video_ids_path):
        preprocess_watch_history()

    print("Authenticating to the Youtube API...")
    youtube = authenticate(config.API_KEY)
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
            video_info_batch = get_video_information(youtube, video_ids)
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