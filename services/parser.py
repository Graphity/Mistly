import requests
from bs4 import BeautifulSoup


def parser(url, tag, name):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    result = soup.find(tag, class_=name).text
    return result
