import pytube
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import requests
import threading

class DownloadManager:
    def __init__(self, progress_bar, quality_var):
        self.video_url = None
        self.playlist_url = None
        self.download_directory = None
        self.stream = None
        self.bytes_downloaded = 0
        self.paused = False
        self.chunk_size = 1024
        self.progress_bar = progress_bar
        self.quality_var = quality_var

    def download(self, url, is_playlist=False):
        if is_playlist:
            playlist = pytube.Playlist(url)
            videos = playlist.video_urls
        else:
            videos = [url]

        for video_url in videos:
            youtube = pytube.YouTube(video_url)
            self.stream = youtube.streams.get_by_resolution(self.quality_var.get())

            response = requests.get(self.stream.url, stream=True)
            total_size = int(response.headers.get('content-length', 0))

            filename = self.stream.default_filename
            if is_playlist:
                filename = f"{playlist.title}/{filename}"

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if self.paused:
                        return

                    if chunk:
                        f.write(chunk)
                        self.bytes_downloaded += len(chunk)
                        self.update_progress(total_size)

        self.progress_bar["value"] = 100

    # ... (other methods remain the same)

def download():
    if playlist_var.get():
        download_manager.start_download(playlist_url_entry.get(), directory_entry.get(), is_playlist=True)
    else:
        download_manager.start_download(video_url_entry.get(), directory_entry.get())

        success_label = tk.Label(root, text="Download complete!")
        success_label.pack()
        root.after(2000, success_label.destroy)  # Remove success message after 2 seconds

        loading_window.destroy()  # Close the loading popup

# ... (rest of the code remains the same)

quality_label = tk.Label(root, text="Select video quality:")
quality_label.pack()

quality_var = tk.StringVar(root)
quality_var.set("720p")  # Default quality
quality_dropdown = ttk.Combobox(root, textvariable=quality_var, values=["144p", "240p", "360p", "480p", "720p", "1080p"])
quality_dropdown.pack()

download_manager = DownloadManager(progress_bar, quality_var)

root.mainloop()
