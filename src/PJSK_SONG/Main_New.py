import os
import shutil
import threading
import time
import tracemalloc

import psutil
import requests
from bs4 import BeautifulSoup


class ResourceMonitor(threading.Thread):
    def __init__(self):
        super().__init__()
        self.max_memory = 0
        self.max_cpu = 0
        self.running = True
        self.daemon = True

    def run(self):
        process = psutil.Process()
        while self.running:
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=0.1)
            self.max_memory = max(self.max_memory, memory_info.rss)
            self.max_cpu = max(self.max_cpu, cpu_percent)
            time.sleep(0.1)

    def stop(self):
        self.running = False


# Constants
type_pre_existing_songs = "pre-existing_songs"
type_cover_songs = "cover_songs"
type_commissioned_songs = "commissioned_songs"
type_contest_songs = "contest_songs"

url_fandom = "https://projectsekai.fandom.com"
url_song_list = "https://projectsekai.fandom.com/wiki/Song_List"


def get_beautiful_soup_requests(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')


def setup():
    print("Setting up...")

    if os.path.exists("songs"):
        print("Removing existing 'songs' directory...")
        shutil.rmtree("songs")

    print("Creating 'songs' directory...")
    os.mkdir("songs")
    print("Creating 'songs/pre-existing_songs' directory...")
    os.mkdir("songs/pre-existing_songs")
    print("Creating 'songs/cover_songs' directory...")
    os.mkdir("songs/cover_songs")
    print("Creating 'songs/commissioned_songs' directory...")
    os.mkdir("songs/commissioned_songs")
    print("Creating 'songs/contest_songs' directory...")
    os.mkdir("songs/contest_songs")

    print("Setup complete!\n")


def fetch():
    pass


def main():
    setup()
    fetch()


def main_with_monitor():
    tracemalloc.start()
    monitor = ResourceMonitor()
    monitor.start()

    main()

    monitor.stop()
    monitor.join()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\nResource usage:")
    print(f"Peak RAM usage (tracemalloc): {peak / 2 ** 20:.2f} MB")
    print(f"Peak RAM usage (psutil): {monitor.max_memory / 2 ** 20:.2f} MB")
    print(f"Peak CPU usage: {monitor.max_cpu:.2f}%")


if __name__ == "__main__":
    main_with_monitor()
