import asyncio
import threading
import time
import tracemalloc

import aiohttp
import psutil
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


async def download_images(hrefs: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, href) for href in hrefs]
        await asyncio.gather(*tasks)


async def download_image(session: aiohttp.ClientSession, url: str):
    print(f"Download: {url}...")
    start = time.time()

    beautiful_soup = await get_beautiful_soup(url)
    infobox = beautiful_soup.find("aside", {"class": "portable-infobox"})

    # Name
    h2 = infobox.find("h2")
    name = h2.text.split("/")[0].strip()

    # Content
    tabber = infobox.find(class_=["wds-tabber"])
    contents = tabber.find_all("div", class_="wds-tab__content", recursive=False)

    # Icon
    content_icon = contents[0]
    content_icon_contents = content_icon.find_all("div", {"class": "wds-tab__content"})
    if content_icon_contents:
        for content in content_icon_contents:
            a = content.find("a")
            icon_title = a["title"]
            icon_href = a["href"]
            file_name = "icon/" + name + "_" + icon_title
            await download_with_session(session, icon_href, file_name, "png")
    else:
        a = content_icon.find("a")
        icon_href = a["href"]
        file_name = "icon/" + name
        await download_with_session(session, icon_href, file_name, "png")

    # Portrait
    content_portrait = contents[1]
    content_portrait_contents = content_portrait.find_all("div", {"class": "wds-tab__content"})
    if content_portrait_contents:
        for content in content_portrait_contents:
            # URL
            a = content.find("a")
            portrait_title = a["title"]
            portrait_href = a["href"]
            file_name = "portrait/" + name + "_" + portrait_title
            await download_with_session(session, portrait_href, file_name, "png")
    else:
        a = content_portrait.find("a")
        portrait_href = a["href"]
        file_name = "portrait/" + name
        await download_with_session(session, portrait_href, file_name, "png")

    end = time.time()
    print(f"Download: {url} finished in {end - start:.2f}s")


async def download_with_session(session: aiohttp.ClientSession, url: str, name: str, type: str):
    file_name = f"{name}.{type}"
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception(f"Failed to fetch image: {file_name} - {response.status}")
        with open(file_name, "wb") as file:
            file.write(await response.read())


def main():
    print("Preparing to download images...")

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

    print("Downloading images...\n")
    start = time.time()

    asyncio.run(download_images(hrefs))

    end = time.time()
    print(f"\nDownload finished in {end - start:.2f}s")


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
