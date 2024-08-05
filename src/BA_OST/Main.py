import asyncio
import re
import time

import aiohttp
import unidecode
from bs4 import BeautifulSoup


async def get_beautiful_soup(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            return BeautifulSoup(await response.text(), "html.parser")


async def download_audios(audio_infos: list):
    tasks = [download_audio(audio_info) for audio_info in audio_infos]
    await asyncio.gather(*tasks)


async def download_audio(audio_info: dict):
    track_name = audio_info["track"]
    track_audio = audio_info["audio"]
    async with aiohttp.ClientSession() as session:
        async with session.get(track_audio) as response:
            print(f"Download: {track_name}...")
            start = time.time()

            if response.status != 200:
                raise Exception(f"Failed to fetch audio: {response.status}")

            with open(f"audio/{track_name}.mp3", "wb") as file:
                file.write(await response.read())

            end = time.time()
            print(f"Download: {track_name} finished in {end - start:.2f}s")


if __name__ == "__main__":
    url = "https://bluearchive.fandom.com/wiki/Soundtrack"

    beautiful_soup = asyncio.run(get_beautiful_soup(url))
    table = beautiful_soup.find("table", {"class": "wikitable"})

    trs = table.find_all("tr")

    audio_infos = []
    track = 0
    artist = ""
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

        src = audio["src"]
        audio_info["audio"] = src

        # Track
        try:
            td = tds[0]
            track = int(td.string)
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

    asyncio.run(download_audios(audio_infos))
