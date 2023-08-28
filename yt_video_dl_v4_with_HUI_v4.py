import pytube
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import requests
import threading

class DownloadManager:
    def __init__(self, progress_bar):
        self.video_url = None
        self.download_directory = None
        self.stream = None
        self.bytes_downloaded = 0
        self.paused = False
        self.chunk_size = 1024
        self.progress_bar = progress_bar

    def download(self):
        youtube = pytube.YouTube(self.video_url)
        self.stream = youtube.streams.filter(progressive=True).get_highest_resolution()

        response = requests.get(self.stream.url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(self.stream.default_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                if self.paused:
                    return

                if chunk:
                    f.write(chunk)
                    self.bytes_downloaded += len(chunk)
                    self.update_progress(total_size)

    def update_progress(self, total_size):
        percent = (self.bytes_downloaded / total_size) * 100
        self.progress_bar["value"] = percent
        root.update_idletasks()

    def start_download(self, video_url, download_directory):
        self.video_url = video_url
        self.download_directory = download_directory
        self.paused = False
        self.bytes_downloaded = 0
        self.download_thread = threading.Thread(target=self.download)
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
    download_manager.start_download(video_url_entry.get(), directory_entry.get())

def pause_resume():
    if download_manager.paused:
        download_manager.paused = False
        pause_resume_button["text"] = "Pause"
    else:
        download_manager.paused = True
        pause_resume_button["text"] = "Resume"

if __name__ == "__main__":
    root = tk.Tk()
    root.title("YouTube Video Downloader")

    video_url_label = tk.Label(root, text="Enter the URL of the YouTube video:")
    video_url_label.pack()

    video_url_entry = tk.Entry(root)
    video_url_entry.pack()

    directory_label = tk.Label(root, text="Select the download directory:")
    directory_label.pack()

    directory_entry = tk.Entry(root)
    directory_entry.pack()

    browse_button = tk.Button(root, text="Browse", command=browse_directory)
    browse_button.pack()

    download_button = tk.Button(root, text="Download Video", command=download)
    download_button.pack()

    pause_resume_button = tk.Button(root, text="Pause", command=pause_resume)
    pause_resume_button.pack()

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack()

    download_manager = DownloadManager(progress_bar)

    root.mainloop()
