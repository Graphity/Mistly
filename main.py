from bs4 import BeautifulSoup
import requests





class Song(Parser):
    def __init__(self, band, song, url, tag, name):
        super().__init__(url, tag, name)
        self.band = band
        self.song = song

    def __repr__(self):
        return (
            f"{self.__class__.__name__} band: {self.band}, song: {self.song}"
        )


def main():
    band_inp = input("Enter band name: ")
    song_inp = input("Enter song name: ")
    band = band_inp.replace(" ", "-")
    song = song_inp.replace(" ", "-")

    url = f"https://genius.com/{band}-{song}-lyrics"

    s = Song(band, song, url, "div", "Lyrics__Container-sc-1ynbvzw-6 jYfhrf")
    print(s.__repr__())
    print(f"Lyric: {s.parse_web()}")


if __name__ == "__main__":
    main()
