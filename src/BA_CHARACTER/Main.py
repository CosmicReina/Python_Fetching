import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup


async def get_beautiful_soup(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")
            return BeautifulSoup(await response.text(), "html.parser")


async def download_images(hrefs: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, href) for href in hrefs]
        await asyncio.gather(*tasks)


async def download_image(session: aiohttp.ClientSession, url: str):
    try:
        print(f"Download: {url}...")
        start = time.time()

        beautiful_soup = await get_beautiful_soup(url)
        portable_infobox = beautiful_soup.find("aside", {"class": "portable-infobox"})

        # Name
        h2 = portable_infobox.find("h2")
        name_full = h2.text
        name = name_full.split("/")[0].strip()

        wds_tab__contents = portable_infobox.find_all("div", {"class": "wds-tab__content"})

        wds_tab__content_icon = wds_tab__contents[0]
        a_icon = wds_tab__content_icon.find("a")
        icon_href = a_icon["href"]
        await download_image_with_session(session, icon_href, f"icon/{name}.png")

        wds_tab__content_portrait = wds_tab__contents[1]
        a_portrait = wds_tab__content_portrait.find("a")
        portrait_href = a_portrait["href"]
        await download_image_with_session(session, portrait_href, f"portrait/{name}.png")

        end = time.time()
        print(f"Download: {url} finished in {end - start:.2f}s")
    except Exception as e:
        print(f"Failed to download: {url} - {e}")


async def download_image_with_session(session: aiohttp.ClientSession, url: str, file_name: str):
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception(f"Failed to fetch image: {response.status}")
        with open(file_name, "wb") as file:
            file.write(await response.read())


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
        hrefs.append(url + href)

    asyncio.run(download_images(hrefs))
