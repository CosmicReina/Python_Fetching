import aiohttp
import asyncio
from bs4 import BeautifulSoup


async def get_beautiful_soup(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            return BeautifulSoup(await response.text(), "html.parser")


async def download_images(hrefs: list[str]):
    tasks = [download_image(href) for href in hrefs]
    await asyncio.gather(*tasks)


async def download_image(url: str):
    pass


if __name__ == "__main__":
    url = "https://bluearchive.fandom.com"
    url_category = "https://bluearchive.fandom.com/wiki/Category:Students"
    beautiful_soup = asyncio.run(get_beautiful_soup(url_category))
    table = beautiful_soup.find("table", {"class": "article-table"})

    trs = table.find_all("tr")[1:]

    hrefs = []
    for tr in trs:
        td = tr.find_all("td")[0]
        a = td.find("a")
        href = a["href"]
        hrefs.append(href)
