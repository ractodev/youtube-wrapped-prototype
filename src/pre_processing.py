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


def extract_video_ids(file_path):
    """
    Extracts video IDs from a Google Takeout watch history HTML file.

    Args:
        - file_path (str): Path to the HTML file containing the watch history.

    Returns:
        - video_ids (list): A list of video IDs extracted from the HTML file.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'lxml')

    video_ids = [link.get('href').split('watch?v=')[1].split(
        '&')[0] for link in soup.find_all('a') if 'watch?v=' in link.get('href', '')]

    print(f"Videos found in watch history: {len(video_ids)}")
    return video_ids


def is_extracted_video_ids_valid(output_file):
    """
    Checks if the cached extracted video IDs are still valid.

    Args:
        - output_file (str): Path to the text file containing the extracted video IDs.

    Returns:
        - valid (bool): True if the cached extracted video IDs are valid, False otherwise.
    """

    if not os.path.exists(output_file):
        return False

    with open(output_file, 'r', encoding='utf-8') as file:
        first_line = file.readline().strip()

    if not first_line:
        return False

    cached_user_id, timestamp_str = first_line.split()
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d-%H-%M-%S')
    current_time = datetime.now()
    time_difference = current_time - timestamp

    if cached_user_id != USER_ID or time_difference.total_seconds() >= 7200:
        return False

    return True


def preprocess_watch_history(input_file='../data/watch_history.html', output_file='../data/extracted_video_ids.txt'):
    """
    Pre-processes the watch history HTML file and extracts video IDs to a text file.

    Args:
        - input_file (str): Path to the watch history HTML file.
        - output_file (str): Path to the text file to save the extracted video IDs.
    """

    print("Starting preprocess_watch_history function...")
    if is_extracted_video_ids_valid(output_file):
        print("Valid pre-processing found, no need to extract new video IDs.")
        return

    try:
        print("Extracting video IDs from Google Takeout watch history...")
        video_ids = extract_video_ids(input_file)
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(f"{USER_ID} {timestamp}\n")
            file.writelines(f"{video_id}\n" for video_id in video_ids)

    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    pre_processing.preprocess_watch_history()
