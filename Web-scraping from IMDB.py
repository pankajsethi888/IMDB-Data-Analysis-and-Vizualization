from bs4 import BeautifulSoup
import requests

#Colletct the movie title and links of top 250 rated movies in IMDB
url = 'http://www.imdb.com/chart/top'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

movies = soup.select('td.titleColumn')
links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]

imdb = {}

base_url = 'http://www.imdb.com'

for i, mvi in enumerate(movies):

    print("Retriving Movie: {}".format(i+1))

    movie_str = mvi.get_text()
    movie = (' '.join(movie_str.split()).replace('.', ''))
    title = movie[len(str(i+1))+1:-7]

    mv_url = base_url + links[i]
    response = requests.get(mv_url)
    soup = BeautifulSoup(response.text, 'lxml')
    json_script = soup.select('script[type="application/ld+json"]')[0].contents[0]

    imdb[title] = json_script

print("Retrived All Top 250 Movies!!!")

# Load data into SQL database
import sqlite3

conn = sqlite3.connect('IMDB_top_250.sqlite')
cur = conn.cursor()

# Setup Tables
cur.executescript('''
                  DROP TABLE IF EXISTS MovieLinks;

                  CREATE TABLE MovieLinks (
                     movie_id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                     movie_name     TEXT UNIQUE,
                     json_script
                );
                  ''')

for name, script in imdb.items():
    cur.execute('''
                INSERT OR IGNORE INTO MovieLinks (
                    movie_name,
                    json_script)
                VALUES (?,?)
                ''', (name, script))
conn.commit()
conn.close()
