import requests
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url, tag, name):
        self.url = url
        self.tag = tag
        self.name = name

    def parse_web(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content, 'html.parser')
        result = soup.find(self.tag, class_=self.name).text
        return result

    def __repr__(self):
        return (
            f"{self.__class__.__name__} url: {self.url}, tag: {self.tag}, name:{self.name}"
        )