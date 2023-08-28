import os
import re
import pytube
import youtube_dl

def extract_video_id(video_url):
    # Check if the URL contains a playlist
    if "playlist" in video_url:
        # Extract the playlist ID from the URL
        playlist_id = re.search(r'list=(.*)', video_url).group(1)
        return playlist_id
    else:
        # Extract the video ID from the URL
        video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', video_url).group(1)
        return video_id

def download_youtube_video(video_url, download_directory, resolution):
    """Downloads a YouTube video to the specified directory.

    Args:
        video_url: The URL of the YouTube video to download.
        download_directory: The directory where the video should be downloaded.
        resolution: The resolution of the video to download.
    """
    try:
        video_id = extract_video_id(video_url)
        youtube = pytube.YouTube(video_id)

        # Filter the streams based on the resolution.
        video_streams = youtube.streams.filter(res=resolution, progressive=True)

        # If no streams at the specified resolution exist, get the highest resolution.
        if not video_streams:
            video_stream = youtube.streams.get_highest_resolution()
        else:
            video_stream = video_streams.first()

        # Download the video to the specified directory.
        video_stream.download(download_directory)

    except pytube.exceptions.AgeRestrictedError as e:
        print(f"The video requires login or is age-restricted: {video_url}")

        # Prompt the user for their login credentials
        username = input("Enter your YouTube username: ")
        password = input("Enter your YouTube password: ")

        # Use youtube-dl to download the video
        ydl_opts = {
            'username': username,
            'password': password,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Download the video
            ydl.download([video_url])

    except pytube.exceptions.VideoUnavailable as e:
        print(f"The video is unavailable: {video_url}")

    except Exception as e:
        print(f"An error occurred while downloading the video: {e}")

def download_youtube_playlist(playlist_url, download_directory, resolution):
    """Downloads a YouTube playlist to the specified directory.

    Args:
    playlist_url: The URL of the YouTube playlist to download.
    download_directory: The directory where the videos should be downloaded.
    resolution: The resolution of the videos to download.
    """
    try:
        playlist_id = extract_video_id(playlist_url)
        playlist = pytube.Playlist(playlist_id)
        playlist_name = re.sub(r'\W+', '-', playlist.title)
        playlist_directory = os.path.join(download_directory, playlist_name)

        if not os.path.exists(playlist_directory):
            os.mkdir(playlist_directory)

        for index, video_url in enumerate(playlist.video_urls, start=1):
            try:
                download_youtube_video(video_url, playlist_directory, resolution)
            except Exception as e:
                print(f"An error occurred while downloading a video in the playlist: {e}")

    except Exception as e:
        print(f"An error occurred while downloading the playlist: {e}")

if __name__ == "__main__":
    option = input(
        "Do you want to download a single video or a playlist? Enter 'video' or 'playlist': ").strip().lower()

    download_directory = input("Enter the directory where the content should be downloaded: ")
    resolution = input("Enter the resolution of the videos (e.g., 720p): ")

    if option == 'video':
        video_url = input("Enter the URL of the YouTube video: ")
        download_youtube_video(video_url, download_directory, resolution)
    elif option == 'playlist':
        playlist_url = input("Enter the URL of the YouTube playlist: ")
        download_youtube_playlist(playlist_url, download_directory, resolution)
    else:
        print("Invalid option. Please run the script again and choose either 'video' or 'playlist'.")
