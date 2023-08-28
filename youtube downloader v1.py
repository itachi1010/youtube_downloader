import pytube

def download_youtube_video(video_url, download_directory):
  """Downloads a YouTube video to the specified directory.

  Args:
    video_url: The URL of the YouTube video to download.
    download_directory: The directory where the video should be downloaded.
  """

  youtube = pytube.YouTube(video_url)

  # Get the highest quality mp4 video stream.
  video_stream = youtube.streams.filter(progressive=True).get_highest_resolution()

  # Download the video to the specified directory.
  video_stream.download(download_directory)


if __name__ == "__main__":
  # Get the video URL from the user.
  video_url = input("Enter the URL of the YouTube video: ")

  # Get the download directory from the user.
  download_directory = input("Enter the directory where the video should be downloaded: ")

  # Download the video.
  download_youtube_video(video_url, download_directory)

