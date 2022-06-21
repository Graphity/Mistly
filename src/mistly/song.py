import requests
import re

from bs4 import BeautifulSoup


class Song:
    def __init__(self, artist: str, title: str, lyrics_url: str) -> None:
        self.artist = artist
        self.title = title
        self.lyrics_url = lyrics_url

    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"

    def fetch_lyrics(self) -> str:
        r = requests.get(self.lyrics_url)
        soup = BeautifulSoup(r.text.replace("<br/>", "\n"), "html.parser")
        lyrics = soup.find("div", id="lyrics-root").text
        junk = ""
        junk += soup.find_all("span", class_="LabelWithIcon__Label-sc-1ri57wg-1")[-1].text
        junk += soup.find_all("div", class_="Button__Container-sc-1874dbw-0")[-1].text
        h2 = soup.find("h2", class_="TextLabel-sc-8kw9oj-0").text
        lyrics = lyrics.replace(junk, "")
        lyrics = lyrics.replace(f"{h2}", "")
        lyrics = re.sub(r"(\[.*?\])*", "", lyrics)
        lyrics = re.sub("\n{3}", "\n\n", lyrics)
        lyrics = lyrics[1:]

        if not lyrics:
            return "No lyrics found"
        return lyrics
