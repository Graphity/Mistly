import requests

from .song import Song

from typing import List


class Genius:
    base_url = "https://api.genius.com"
    
    def __init__(self, access_token: str) -> None:
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.validate()

    def validate(self) -> None:
        endpoint = f"{self.base_url}/account"
        r = requests.get(endpoint, headers=self.headers)

        if r.status_code == 403:
            raise Exception("Authorization Failed: Access Token is invalid")

    def search(self, query: str) -> List[Song]:
        endpoint = f"{self.base_url}/search"
        params = {"q": query}
        r = requests.get(endpoint, params=params, headers=self.headers)
        songs = []

        for hit in r.json()["response"]["hits"]:
            songs.append(Song(hit["result"]["artist_names"],
                              hit["result"]["title"],
                              hit["result"]["url"]))
        return songs
