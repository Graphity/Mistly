from bs4 import BeautifulSoup
import requests


band_inp = input("Enter band name: ")
song_inp = input("Enter song name: ")
band = band_inp.replace(" ", "-")
song = song_inp.replace(" ", "-")

url = f"https://genius.com/{band}-{song}-lyrics"
r = requests.get(url, 'html.parser')
soup = BeautifulSoup(r.content)
result = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-6 jYfhrf").text

