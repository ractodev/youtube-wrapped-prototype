from bs4 import BeautifulSoup

def extract_video_ids(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'lxml')

    video_ids = []
    for idx, link in enumerate(soup.find_all('a')):
        url = link.get('href')
        if 'watch?v=' in url:
            video_id = url.split('watch?v=')[1].split('&')[0]
            video_ids.append(video_id)

    print(f"Videos found in watch history: {len(video_ids)}")
    return video_ids

def save_video_ids(video_ids, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for video_id in video_ids:
            file.write(f"{video_id}\n")

def preprocess_watch_history(input_file='history/watch-history.html', output_file='history/extracted_video_ids.txt'):
    print("Extracting video IDs from Google Takeout watch history...")
    video_ids = extract_video_ids(input_file)
    save_video_ids(video_ids, output_file)

if __name__ == "__main__":
    preprocess_watch_history()