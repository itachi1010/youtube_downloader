import re
import threading
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pytube
import requests

class DownloadManager:
    def __init__(self, progress_bar, quality_var, error_text_widget):
        self.video_url = None
        self.download_directory = None
        self.stream = None
        self.bytes_downloaded = 0
        self.paused = False
        self.chunk_size = 1024
        self.progress_bar = progress_bar
        self.quality_var = quality_var
        self.error_text_widget = error_text_widget


    def ensure_directory_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def download(self, url, is_playlist=False):
        try:
            if is_playlist:
                playlist = pytube.Playlist(url)
                playlist_name = re.sub(r'\W+', '-', playlist.title)
                playlist_directory = os.path.join(self.download_directory, playlist_name)

                self.ensure_directory_exists(playlist_directory)

                for idx, video_url in enumerate(playlist.video_urls, start=1):
                    youtube = pytube.YouTube(video_url)
                    video_stream = youtube.streams.get_highest_resolution()

                    response = requests.get(video_stream.url, stream=True)
                    total_size = int(response.headers.get('content-length', 0))

                    video_title_cleaned = re.sub(r'\W+', '-', youtube.title)
                    video_filename = f"{idx:02d} - {video_title_cleaned}.mp4"
                    video_path = os.path.join(playlist_directory, video_filename)

                    with open(video_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if self.paused:
                                return

                            if chunk:
                                f.write(chunk)
                                self.bytes_downloaded += len(chunk)
                                self.update_progress(total_size)

                self.progress_bar["value"] = 100

        except Exception as e:
            error_message = f"Error during download: {str(e)}\n"
            self.error_text_widget.insert(tk.END, error_message)

    def update_progress(self, total_size):
        total_size = int(total_size)  # Convert to integer
        percent = (self.bytes_downloaded / total_size) * 100
        self.progress_bar["value"] = percent
        root.update_idletasks()

    def start_download(self, url, download_directory, is_playlist):
        self.video_url = url  # Store the video URL
        self.download_directory = download_directory
        self.paused = False
        self.bytes_downloaded = 0
        self.download_thread = threading.Thread(target=self.download,
                                                args=(self.video_url, is_playlist))
        self.download_thread.start()
        self.show_loading_bar()

    def show_loading_bar(self):
        loading_window = tk.Toplevel(root)
        loading_window.title("Downloading...")

        loading_label = tk.Label(loading_window, text="Downloading video...")
        loading_label.pack()

        percentage_label = tk.Label(loading_window, text="0%")
        percentage_label.pack()

        size_label = tk.Label(loading_window, text="0 MB / 0 MB")
        size_label.pack()

        loading_progress_bar = ttk.Progressbar(loading_window, orient="horizontal", length=300, mode="indeterminate")
        loading_progress_bar.pack()
        loading_progress_bar.start()

        self.update_labels(percentage_label, size_label, loading_window)

        if not self.download_thread.is_alive():
            loading_window.destroy()

    def update_labels(self, percentage_label, size_label, loading_window):
        if self.bytes_downloaded > 0 and self.stream:
            total_size = self.stream.filesize
            percent = (self.bytes_downloaded / total_size) * 100
            downloaded_mb = self.bytes_downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            remaining_mb = total_mb - downloaded_mb

            percentage_label.config(text=f"{percent:.2f}%")
            size_label.config(text=f"{downloaded_mb:.2f} MB / {total_mb:.2f} MB\nRemaining: {remaining_mb:.2f} MB")

        if self.download_thread.is_alive():
            root.after(500, self.update_labels, percentage_label, size_label, loading_window)
        else:
            loading_window.destroy()



def browse_directory():
    download_directory = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(0, download_directory)

def download():
    is_playlist = playlist_var.get()
    download_manager.start_download(link_entry.get(),
    directory_entry.get(), is_playlist=is_playlist)


def pause_resume():
    if download_manager.paused:
        download_manager.paused = False
        pause_resume_button["text"] = "Pause"
    else:
        download_manager.paused = True
        pause_resume_button["text"] = "Resume"


if __name__ == "__main__":
    def refresh():
        # Clear the error text widget
        error_text_widget.delete(1.0, tk.END)
        # Reset progress bar
        progress_bar["value"] = 0
        # Clear the link entry
        link_entry.delete(0, tk.END)
        # Uncheck the playlist checkbox
        playlist_var.set(0)
        # Enable download button
        download_button.config(state=tk.NORMAL)
        # Stop and join the download thread if it's still running
        if download_manager.download_thread.is_alive():
            download_manager.paused = True
            download_manager.download_thread.join()

    root = tk.Tk()
    root.title("YouTube Video Downloader")

    link_label = tk.Label(root, text="Enter the URL:")
    link_label.pack()

    link_entry = tk.Entry(root)
    link_entry.pack()

    playlist_var = tk.IntVar()
    playlist_checkbutton = tk.Checkbutton(root, text="Download Playlist", variable=playlist_var)
    playlist_checkbutton.pack()

    directory_label = tk.Label(root, text="Select the download directory:")
    directory_label.pack()

    directory_entry = tk.Entry(root)
    directory_entry.pack()

    browse_button = tk.Button(root, text="Browse", command=browse_directory)
    browse_button.pack()

    download_button = tk.Button(root, text="Download", command=download)
    download_button.pack()

    refresh_button = tk.Button(root, text="Refresh", command=refresh)
    refresh_button.pack()

    pause_resume_button = tk.Button(root, text="Pause", command=pause_resume)
    pause_resume_button.pack()

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack()

    quality_label = tk.Label(root, text="Select video quality:")
    quality_label.pack()

    quality_var = tk.StringVar(root)
    quality_var.set("720p")  # Default quality

    quality_dropdown = ttk.Combobox(root, textvariable=quality_var, values=["144p", "240p", "360p", "480p", "720p", "1080p"])
    quality_dropdown.pack()

    error_text_widget = tk.Text(root, height=6, width=50)
    error_text_widget.pack()

    download_manager = DownloadManager(progress_bar, quality_var, error_text_widget)
    root.mainloop()