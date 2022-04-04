from classes.song.song import Song


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
