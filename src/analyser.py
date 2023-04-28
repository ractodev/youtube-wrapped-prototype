# autopep8: off
# Necessary imports
import os
import sys

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pre_processing import parse_watch_history
from config.credentials import * 
from utils.imports import * 
# autopep8: on

def get_total_watch_time(watch_history):
    total_duration = 0
    for video_id, video_data in watch_history.items():
        video_duration = isodate.parse_duration(video_data['duration'])
        total_duration += video_duration.total_seconds() / 60.0
        
    return int(total_duration)

def get_toplist(full_video_data, key, n):
    toplist = []
    views = {}
    for video_id, video_data in full_video_data.items():
        if video_data[key]:
            views[video_data[key]] = views.get(video_data[key], 0) + 1
    for key_value, count in sorted(views.items(), key=lambda x: x[1], reverse=True):
        toplist.append([key_value, count])
    return toplist[:n]


if __name__ == "__main__":
    data = {'f3DfJxvkN-8': {'title': 'Tittade på AirPods Pro 2 Review: 1 Underrated Thing!', 'channel': 'Marques Brownlee', 'duration': None, 'category': None, 'url': 'https://www.youtube.com/watch?v=f3DfJxvkN-8', 'ttl': None}, 'h0QLtup0CWQ': {'title': 'Tittade på Active Directory Tutorial for Beginners - Live Training', 'channel': 'Server Academy', 'duration': None, 'category': None, 'url': 'https://www.youtube.com/watch?v=h0QLtup0CWQ', 'ttl': None}, 'xi_VkbbZqpA': {'title': 'Tittade på Uninstall Movavi Video Suite 18 in Windows 10', 'channel': 'How-toUninstall', 'duration': None, 'category': None, 'url': 'https://www.youtube.com/watch?v=xi_VkbbZqpA', 'ttl': None}}
    print(get_toplist(data, 'title', 5))
    print(get_toplist(data, 'channel', 5))
