import asyncio
import os
import shutil

import aiohttp
from bs4 import BeautifulSoup


# Constants
type_pre_existing_songs = "pre-existing_songs"
type_cover_songs = "cover_songs"
type_commissioned_songs = "commissioned_songs"
type_contest_songs = "contest_songs"


async def get_beautiful_soup(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            return BeautifulSoup(await response.text(), "html.parser")


async def fetch_song(url: str, song_type: str):
    beautiful_soup = asyncio.run(get_beautiful_soup(url))
    article_table = beautiful_soup.find_all("table", class_="article-table")
    trs_song = []
    for table in article_table:
        trs = table.find_all("tr")
        for tr in trs[1:]:
            trs_song.append(tr)

    for tr in trs_song:
        no = tr.find_all("td")[0].text
        title = tr.find_all("td")[1].text
        song = tr.find_all("td")[-1].find("audio")


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
    url_fandom = "https://projectsekai.fandom.com"
    list_songs = []
    trs = wikitable.find_all("tr")[1:]
    for tr in trs:
        td = tr.find_all("td")[0]
        a = td.find("a")
        url = url_fandom + a["href"]
        list_songs.append({
            "type_song": type_song,
            "url": url
        })
    return list_songs


def main():
    setup()

    url_song_list = "https://projectsekai.fandom.com/wiki/Song_List"
    beautiful_soup = asyncio.run(get_beautiful_soup(url_song_list))
    wikitables = beautiful_soup.find_all("table", class_="wikitable")

    pre_existing_songs = wikitables[0]
    cover_songs = wikitables[1]
    commissioned_songs = wikitables[2]
    contest_songs = wikitables[3]

    list_pre_existing_songs = get_list_songs_of_type(pre_existing_songs, type_pre_existing_songs)
    list_cover_songs = get_list_songs_of_type(cover_songs, type_cover_songs)
    list_commissioned_songs = get_list_songs_of_type(commissioned_songs, type_commissioned_songs)
    list_contest_songs = get_list_songs_of_type(contest_songs, type_contest_songs)

    list_total_songs = list_pre_existing_songs + list_cover_songs + list_commissioned_songs + list_contest_songs

    print("\n".join([str(song) for song in list_total_songs]))


if __name__ == "__main__":
    main()
