"""
pre_processing.py:

This module extracts video IDs from a Google Takeout watch history HTML file
and saves them to a text file. The extracted video IDs can be used to retrieve
video information from the YouTube API for future runs, thus speeding up the program.

Functions:
    - extract_video_ids(): Extracts video IDs from a Google Takeout watch history HTML file.
    - save_video_ids(): Saves a list of video IDs to a text file.
    - preprocess_watch_history(): Orchestrates the extracting- and writing process.
"""

# Necessary imports
import os
import sys

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.imports import *


def extract_video_ids(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'lxml')

    video_ids = [link.get('href').split('watch?v=')[1].split('&')[0] for link in soup.find_all('a') if 'watch?v=' in link.get('href', '')]

    print(f"Videos found in watch history: {len(video_ids)}")
    return video_ids

def save_video_ids(video_ids, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(f"{video_id}\n" for video_id in video_ids)

def preprocess_watch_history():
    input_file='../data/watch_history.html'
    output_file='../data/extracted_video_ids.txt'
    try:
        print("Extracting video IDs from Google Takeout watch history...")
        video_ids = extract_video_ids(input_file)
        save_video_ids(video_ids, output_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    preprocess_watch_history()
