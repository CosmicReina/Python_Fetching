import asyncio
import os
import shutil
import time

import aiohttp
from bs4 import BeautifulSoup


# Constants
type_pre_existing_songs = "pre-existing_songs"
type_cover_songs = "cover_songs"
type_commissioned_songs = "commissioned_songs"
type_contest_songs = "contest_songs"

url_fandom = "https://projectsekai.fandom.com"
url_song_list = "https://projectsekai.fandom.com/wiki/Song_List"


async def get_beautiful_soup(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            return BeautifulSoup(await response.text(), "html.parser")


async def fetch_songs(list_songs: list):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch_song(session, song["url"], song["type_song"])) for song in list_songs]
        finished, unfinished = await asyncio.wait(tasks)
        print(f"\nSongs finished: {len(finished)}")
        print(f"Songs unfinished: {len(unfinished)}")


async def fetch_song(session: aiohttp.ClientSession, url: str, type_song: str):
    print(f"Download: {url}...")
    start = time.time()

    beautiful_soup = await get_beautiful_soup(url)
    article_table = beautiful_soup.find_all("table", class_="article-table")

    song_title = beautiful_soup.find("h2", class_="pi-title").text
    if song_title is None:
        return

    unit_div = beautiful_soup.find("div", attrs={"data-source": "unit"})
    song_artist = unit_div.find("b").find("a").text

    trs_song = []
    for table in article_table:
        trs = table.find_all("tr")
        for tr in trs[1:]:
            trs_song.append(tr)

    file_directory = f"songs/{type_song}/{song_artist} - {song_title}"
    if len(trs_song) != 0:
        os.mkdir(file_directory)

    for tr in trs_song:
        no = tr.find_all("td")[0].text.strip()
        title = tr.find_all("td")[1].text.strip()
        song = tr.find_all("td")[-1].find("audio")
        src = song["src"]

        name = f"{no} - {title}"
        if song is not None:
            await download_with_session(session, src, f"{file_directory}/{name}", "mp3")
        else:
            print(f"Failed to download: {name}")
            return

    end = time.time()
    print(f"Download: {url} finished in {end - start:.2f}s")


async def download_with_session(session: aiohttp.ClientSession, url: str, name: str, type: str):
    async with session.get(url) as response:
        file_name = f"{name}.{type}"
        if response.status != 200:
            raise Exception(f"Failed to fetch image: {file_name} - {response.status}")
        with open(file_name, "wb") as file:
            file.write(await response.read())


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


def get_list_songs_of_type(wikitable: BeautifulSoup, type_song: str) -> list:
    return [{
        "type_song": type_song,
        "url": url_fandom + tr.find_all("td")[0].find("a")["href"]
    } for tr in wikitable.find_all("tr")[1:]]


def main():
    setup()

    beautiful_soup = asyncio.run(get_beautiful_soup(url_song_list))
    wikitables = beautiful_soup.find_all("table", class_="wikitable")

    # pre_existing_songs = wikitables[0]
    # cover_songs = wikitables[1]
    # commissioned_songs = wikitables[2]
    # contest_songs = wikitables[3]
    #
    # list_pre_existing_songs = get_list_songs_of_type(pre_existing_songs, type_pre_existing_songs)
    # list_cover_songs = get_list_songs_of_type(cover_songs, type_cover_songs)
    # list_commissioned_songs = get_list_songs_of_type(commissioned_songs, type_commissioned_songs)
    # list_contest_songs = get_list_songs_of_type(contest_songs, type_contest_songs)
    #
    # list_total_songs = list_pre_existing_songs + list_cover_songs + list_commissioned_songs + list_contest_songs
    # songs_amount = len(list_total_songs)
    # print(f"Fetching {songs_amount} songs...")

    # Test
    asyncio.run(fetch_songs([{
        "type_song": type_commissioned_songs,
        "url": "https://projectsekai.fandom.com/wiki/Kitty"
    }]))


if __name__ == "__main__":
    main()
