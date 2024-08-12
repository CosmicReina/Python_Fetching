import asyncio

import aiohttp
from bs4 import BeautifulSoup


async def get_beautiful_soup(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            return BeautifulSoup(await response.text(), "html.parser")


def main():
    url = "https://projectsekai.fandom.com/wiki/Song_List"
    beautiful_soup = asyncio.run(get_beautiful_soup(url))
    wikitables = beautiful_soup.find_all("table", class_="wikitable")
    pre_existing_songs = wikitables[0]
    cover_songs = wikitables[1]
    commissioned_songs = wikitables[2]
    trs = commissioned_songs.find_all("tr")
    print(len(trs))
    contest_songs = wikitables[3]


if __name__ == "__main__":
    main()
