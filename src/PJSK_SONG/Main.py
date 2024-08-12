import asyncio
import os
import shutil

import aiohttp
from bs4 import BeautifulSoup


async def get_beautiful_soup(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            return BeautifulSoup(await response.text(), "html.parser")


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


def main():
    setup()

    url = "https://projectsekai.fandom.com/wiki/Song_List"
    beautiful_soup = asyncio.run(get_beautiful_soup(url))
    wikitables = beautiful_soup.find_all("table", class_="wikitable")
    pre_existing_songs = wikitables[0]
    cover_songs = wikitables[1]
    commissioned_songs = wikitables[2]
    contest_songs = wikitables[3]


if __name__ == "__main__":
    main()
