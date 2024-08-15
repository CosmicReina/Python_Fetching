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


def get_list_song_of_type(wikitable: BeautifulSoup, type: str) -> list:
    return [{
        "type_song": type,
        "url": url_fandom + tr.find_all("td")[0].find("a")["href"]
    } for tr in wikitable.find_all("tr")[1:]]


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
    beautiful_soup = get_beautiful_soup_requests(url_song_list)
    wikitables = beautiful_soup.find_all("table", class_="wikitable")

    pre_existing_songs = wikitables[0]
    cover_songs = wikitables[1]
    commissioned_songs = wikitables[2]
    contest_songs = wikitables[3]

    list_pre_existing_songs = get_list_song_of_type(pre_existing_songs, type_pre_existing_songs)
    list_cover_songs = get_list_song_of_type(cover_songs, type_cover_songs)
    list_commissioned_songs = get_list_song_of_type(commissioned_songs, type_commissioned_songs)
    list_contest_songs = get_list_song_of_type(contest_songs, type_contest_songs)

    list_total_songs = list_pre_existing_songs + list_cover_songs + list_commissioned_songs + list_contest_songs
    print("\n".join([str(song) for song in list_total_songs]))


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
