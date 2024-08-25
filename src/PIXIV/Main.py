import aiohttp
from rich.progress import Progress
from bs4 import BeautifulSoup
import os
import shutil
import asyncio


# Constants
headers = {
    'Referer': 'https://accounts.pixiv.net/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

url = "https://www.pixiv.net/"
url_search = "https://www.pixiv.net/en/tags/"

# Functions
async def get_beautiful_soup(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"Failed to get {url}")
                return None
            return BeautifulSoup(await response.text(), "html.parser")


def setup():
    print("Setting up...")

    if os.path.exists("image"):
        print("Removing existing 'image' directory...")
        shutil.rmtree("image")

    print("Creating 'image' directory...")
    os.mkdir("image")


def main():
    setup()


if __name__ == "__main__":
    main()
