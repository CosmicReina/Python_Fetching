import aiohttp
import asyncio
from bs4 import BeautifulSoup


async def get_beautiful_soup(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            return BeautifulSoup(await response.text(), "html.parser")


if __name__ == "__main__":
    url_wiki = "https://bluearchive.fandom.com/wiki/"
    url_category = "https://bluearchive.fandom.com/wiki/Category:Students"
    beautiful_soup = asyncio.run(get_beautiful_soup(url_category))
    table = beautiful_soup.find("table", {"class": "article-table"})
    trs = table.find_all("tr")[1:]
    for tr in trs:
        td = tr.find_all("td")[0]
        a = td.find("a")
        href = a["href"]
        print(href)
