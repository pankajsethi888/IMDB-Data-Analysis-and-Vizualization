from bs4 import BeautifulSoup
import requests

#Colletct the movie title and links of top 250 rated movies in IMDB
url = 'http://www.imdb.com/chart/top'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

movies = soup.select('td.titleColumn')
links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]

imdb = {}

for i, mvi in enumerate(movies):
    movie_str = mvi.get_text()
    movie = (' '.join(movie_str.split()).replace('.', ''))
    title = movie[len(str(i+1))+1:-7]

    imdb[title] = links[i]

print(imdb)
