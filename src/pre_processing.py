"""
pre_processing.py:

This module extracts video IDs from a Google Takeout watch history HTML file
and saves them to a text file. The extracted video IDs can be used to retrieve
video information from the YouTube API for future runs, thus speeding up the program.
"""

# autopep8: off
# Necessary imports
import os
import sys

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.imports import *
from config.credentials import *
# autopep8: on

# Define the input file path
INPUT_FILE_PATH = '../data/watch_history.json'


def parse_watch_history():
    try:
        with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as file:
            watch_history_data = json.load(file)
    except FileNotFoundError:
        logging.error(f'File "{INPUT_FILE_PATH}" not found.')
        return {}

    parsed_watch_history = {}
    required_parameters = ['title', 'titleUrl', 'subtitles']
    for entry in watch_history_data:
        if all(param in entry for param in required_parameters) and entry['subtitles'][0]['name']:
            video_id = urlparse(entry['titleUrl']).query.split('=')[-1]
            video_data = {
                'title': entry['title'],
                'channel': entry['subtitles'][0]['name'],
                'duration': None,
                'category': None,
                'url': entry['titleUrl'],
                'ttl': None
            }
            parsed_watch_history[video_id] = video_data

    return parsed_watch_history
