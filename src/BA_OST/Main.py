import aiohttp
import requests
from bs4 import BeautifulSoup

url = "https://bluearchive.fandom.com/wiki/Soundtrack"

response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Failed to fetch page: {response.status_code}")

beautiful_soup = BeautifulSoup(response.text, "html.parser")
table = beautiful_soup.find("table", {"class": "wikitable"})
if table is None:
    raise Exception("Failed to find table")

trs = table.find_all("tr")

audio_infos = []
track = 0
artist = ""
for tr in trs[2:]:
    info_keys = ["track", "audio"]
    audio_info = dict.fromkeys(info_keys)
    tds = tr.find_all("td")

    # Audio
    td_audio = tds[-1]
    audio = td_audio.find("audio")

    if audio is None:
        continue

    src = audio["src"]
    audio_info["audio"] = src

    # Track
    try:
        td = tds[0]
        text = td.text
        track = int(text)
        has_track_info = True
    except ValueError:
        has_track_info = False

    # Artist
    if len(tds) > 2:
        artist = tds[2].text.strip()

    if has_track_info:
        td_track = tds[0:-1]
        track_name = " - ".join([td.find(text=True, recursive=False).strip() for td in td_track])
    else:
        td_track = tds[0:-1]
        track_name = " - ".join(
            [str(track)] + [td.find(text=True, recursive=False).strip() for td in td_track] + [artist])
    audio_info["track"] = track_name

    # Append to list
    audio_infos.append(audio_info)

for audio_info in audio_infos:
    print(audio_info)
