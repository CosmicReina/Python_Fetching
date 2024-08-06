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
        infobox = beautiful_soup.find("aside", {"class": "portable-infobox"})
        # print(infobox)

        # Name
        h2 = infobox.find("h2")
        name = h2.text.split("/")[0].strip()

        tabber = infobox.find("section", {"class": "wds-tabber"})

        contents = tabber.find_all("div", class_="wds-tab__content", recursive=False)
        # print("\n\n".join([str(wds_tab__content) for wds_tab__content in contents]))
        # print(contents)

        # Icon
        content_icon = contents[0]
        # print(content_icon)
        content_icon_contents = content_icon.find_all("div", {"class": "wds-tab__content"})
        if content_icon_contents:
            for content in content_icon_contents:
                a = content.find("a")
                icon_href = a["href"]
                print(icon_href)
        else:
            a = content_icon.find("a")
            icon_href = a["href"]
            print(icon_href)

        # Portrait
        content_portrait = contents[1]
        # print(content_portrait)
        content_portrait_contents = content_portrait.find_all("div", {"class": "wds-tab__content"})
        if content_portrait_contents:
            for content in content_portrait_contents:
                a = content.find("a")
                portrait_href = a["href"]
                print(portrait_href)
        else:
            a = content_portrait.find("a")
            portrait_href = a["href"]
            print(portrait_href)


        # print("1.")
        # # print(contents[0])
        #
        # print("2.")
        # # print(contents[1])
        #
        # wds_tab__contents_contents = contents[1].find_all("div", {"class": "wds-tab__content"})
        # print("\n\n".join([str(wds_tab__content) for wds_tab__content in wds_tab__contents_contents]))


        # Contents
        # tabber = infobox.find_all("div", {"class": "wds-tabber"})[0]
        # print(tabber)
        # contents = tabber.find_all("div", {"class": "wds-tab__content"})
        #
        # # Icon
        # wds_tab__content_icon = contents[0]
        # a_icon = wds_tab__content_icon.find("a")
        # icon_href = a_icon["href"]
        # print(icon_href)
        #
        # # Portrait
        # wds_tab__content_portrait = contents[1]
        # print(wds_tab__content_portrait)

        # # Portrait
        # wds_tab__content_portrait = contents[1]
        # print(wds_tab__content_portrait)
        # pi_image_collection = wds_tab__content_portrait.find("div", {"class": "pi-image-collection"})
        # if pi_image_collection:
        #     print("Case 1")
        #     wds_tab__content_portraits = pi_image_collection.find_all("div", {"class": "wds-tab__content"})
        #     print(len(wds_tab__content_portraits))
        #     for wds_tab__content_portrait in wds_tab__content_portraits:
        #         a_portrait = wds_tab__content_portrait.find("a")
        #         portrait_href = a_portrait["href"]
        #         print(portrait_href)
        # else:
        #     print("Case 2")
        #     a_portrait = wds_tab__content_portrait.find("a")
        #     portrait_href = a_portrait["href"]
        #     print(portrait_href)

        # contents = infobox.find_all("div", {"class": "wds-tab__content"})
        #
        # wds_tab__content_icon = contents[0]
        # print(wds_tab__content_icon)
        # a_icon = wds_tab__content_icon.find("a")
        # icon_href = a_icon["href"]
        # await download_image_with_session(session, icon_href, f"icon/{name}.png")
        #
        # print("\n\n")
        #
        # wds_tab__content_portrait = contents[1]
        # print(wds_tab__content_portrait)
        # a_portrait = wds_tab__content_portrait.find("a")
        # portrait_href = a_portrait["href"]
        # await download_image_with_session(session, portrait_href, f"portrait/{name}.png")

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

    # asyncio.run(download_images(hrefs))
    # asyncio.run(download_images(["https://bluearchive.fandom.com/wiki/Aikiyo_Fuuka_(New_Year_ver.)"]))
    # asyncio.run(download_images(["https://bluearchive.fandom.com/wiki/Wanibuchi_Akari"]))
    asyncio.run(download_images(["https://bluearchive.fandom.com/wiki/Hayase_Yuuka"]))
