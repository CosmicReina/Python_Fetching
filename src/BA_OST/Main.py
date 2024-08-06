import asyncio
import re
import threading
import time
import tracemalloc

import aiohttp
import psutil
import unidecode
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


async def get_beautiful_soup(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            return BeautifulSoup(await response.text(), "html.parser")


async def download_audios(audio_infos: list):
    async with aiohttp.ClientSession() as session:
        tasks = [download_audio(session, audio_info) for audio_info in audio_infos]
        await asyncio.gather(*tasks)


async def download_audio(session: aiohttp.ClientSession, audio_info: dict):
    track_name = audio_info["track"]
    track_audio = audio_info["audio"]
    async with session.get(track_audio) as response:
        print(f"Download: {track_name}...")
        start = time.time()

        if response.status != 200:
            raise Exception(f"Failed to fetch audio: {response.status}")

        with open(f"audio/{track_name}.mp3", "wb") as file:
            file.write(await response.read())

        end = time.time()
        print(f"Download: {track_name} finished in {end - start:.2f}s.")


def main():
    print("Preparing to download audio files...")

    url = "https://bluearchive.fandom.com/wiki/Soundtrack"

    beautiful_soup = asyncio.run(get_beautiful_soup(url))
    table = beautiful_soup.find("table", {"class": "wikitable"})

    trs = table.find_all("tr")

    track = 0
    artist = ""
    audio_infos = []
    for tr in trs[2:]:
        # Dict
        info_keys = ["track", "audio"]
        audio_info = dict.fromkeys(info_keys)
        tds = tr.find_all("td")

        # Audio
        td_audio = tds[-1]
        audio = td_audio.find("audio")

        if audio is None:
            continue

        audio_info["audio"] = audio["src"]

        # Track
        try:
            track = int(tds[0].string)
            has_track = True
        except ValueError:
            has_track = False

        # Artist
        if has_track and len(tds) > 2:
            artist = tds[2].string.strip()

        # Track name
        if has_track:
            td_track = tds[0:-1]
            track_name = " - ".join([td.find(string=True, recursive=False).strip() for td in td_track])
        else:
            td_track = tds[0:-1]
            if len(td_track) > 1:
                track_name = " - ".join(
                    [str(track)] + [td.find(string=True, recursive=False).strip() for td in td_track])
            else:
                track_name = " - ".join(
                    [str(track)] + [td.find(string=True, recursive=False).strip() for td in td_track] + [artist])
        track_name = unidecode.unidecode(track_name)
        track_name = re.sub(r"[^a-zA-Z0-9()\-\s]", "", track_name)
        audio_info["track"] = track_name

        # Append to list
        audio_infos.append(audio_info)

    print("Downloading audio files...\n")
    start = time.time()

    asyncio.run(download_audios(audio_infos))

    end = time.time()
    print(f"\nDownload finished in {end - start:.2f}s.")


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
