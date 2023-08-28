import os
import re
from pytube import Playlist, YouTube


def download_youtube_video(video_url, download_directory, resolution):
    """Downloads a YouTube video to the specified directory.

    Args:
        video_url: The URL of the YouTube video to download.
        download_directory: The directory where the video should be downloaded.
        resolution: The resolution of the video to download.
    """
    youtube = YouTube(video_url)

    # Filter the streams based on the resolution.
    video_streams = youtube.streams.filter(res=resolution, progressive=True)

    # If no streams at the specified resolution exist, get the highest resolution.
    if not video_streams:
        video_stream = youtube.streams.get_highest_resolution()
    else:
        video_stream = video_streams.first()

    # Download the video to the specified directory.
    video_stream.download(download_directory)


def download_youtube_playlist(playlist_url, download_directory, resolution):
    """Downloads a YouTube playlist to the specified directory.

    Args:
    playlist_url: The URL of the YouTube playlist to download.
    download_directory: The directory where the videos should be downloaded.
    resolution: The resolution of the videos to download.
    """

    playlist = Playlist(playlist_url)
    playlist_name = re.sub(r'\W+', '-', playlist.title)
    playlist_directory = os.path.join(download_directory, playlist_name)

    if not os.path.exists(playlist_directory):
        os.mkdir(playlist_directory)

    for index, video_url in enumerate(playlist.video_urls, start=1):
        youtube = YouTube(video_url)

        # Filter the streams based on the resolution.
        video_streams = youtube.streams.filter(res=resolution, progressive=True)

        # If no streams at the specified resolution exist, get the highest resolution.
        if not video_streams:
            video_stream = youtube.streams.get_highest_resolution()
        else:
            video_stream = video_streams.first()

        # Generate the filename.
        video_filename = f"{index}. {video_stream.default_filename}"

        # Download the video to the specified directory.
        video_stream.download(playlist_directory, filename=video_filename)


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
