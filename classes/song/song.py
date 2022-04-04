from classes.parser.parser import Parser


class Song(Parser):
    def __init__(self, band: str, song: str, url: str, tag: str, name: str):
        super().__init__(url, tag, name)
        self.band = band
        self.song = song

    def __repr__(self):
        return (
            f"({self.__class__.__name__} band: {self.band}, song: {self.song})"
        )
