# YouTube Watch Time Analyzer

This project helps you analyze your YouTube watch history, such as calculating the total watch time and listing the top 10 most-watched videos. To use this project, you need to obtain your watch history from Google Takeout, set up a YouTube Data API key, and set up a Firebase Realtime Database.

_Note: Since there is currently no YouTube API that allows insights on a user's actual watch time, the entire video duration is considered._

## Prerequisites

### Google Takeout

1. Visit [Google Takeout](https://takeout.google.com/settings/takeout).
2. Select only "YouTube and YouTube Music" by deselecting all other services.
3. Click on "All YouTube and YouTube Music data included" and deselect all other options except "history" > "watch-history.html".
4. Click "Next step" and then click "Create export".
5. Download the generated archive when it's ready.
6. Extract the `watch-history.html` file from the archive and place it in the `history` folder of this project.

### YouTube Data API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with your Google account.
3. Click on "Select a project" in the top-right corner, and then click on "New Project" to create a new project.
4. Enter a project name, and then click "Create".
5. Navigate to the [YouTube Data API v3 Dashboard](https://console.cloud.google.com/apis/library/youtube.googleapis.com).
6. Click "Enable" to enable the API for your project.
7. Click "Create Credentials" and follow the instructions to create an API key.

### Firebase Realtime Database

1. Visit [Firebase Console](https://console.firebase.google.com/).
2. Sign in with your Google account.
3. Click on "Add project" and create a new project.
4. In the left-hand menu, click on "Realtime Database" and then click "Create database".
5. Choose a location for your database and click "Enable".
6. In the "Project settings" (gear icon) in the top-left corner, click on "General" and scroll down to "Your apps". Click on the "</>" icon to add a web app.
7. Copy the "apiKey" from the provided config object. This will be your Firebase API key.

## Setup

1. Clone this repository.
2. Create a `config.py` file in the `config` folder with the following content:

```python
YOUTUBE_API_KEY = 'your-youtube-api-key-here'
FIREBASE_DB_URL = 'your-firebase-db-url-here'
FIREBASE_API_KEY = 'your-firebase-api-key-here'
```

3. Run `pip install -r requirements.txt` to install the required packages.

## Usage

1. Make sure your `watch-history.html` file is placed in the history folder.
2. Make sure you have created a `config.py` containing your API key, and that it's placed in the config folder.
3. Run `python watch_times.py` in your terminal or command prompt. The script will process your watch history and display the results.
