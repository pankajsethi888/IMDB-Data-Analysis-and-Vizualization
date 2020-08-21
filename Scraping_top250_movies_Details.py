
from bs4 import BeautifulSoup
import requests
import sqlite3
import json

conn = sqlite3.connect('IMDB_top_250.sqlite')
cur = conn.cursor()

cur.executescript('''
                  DROP TABLE IF EXISTS ContentRateList;
                  DROP TABLE IF EXISTS MovieDetails;

                  CREATE TABLE IF NOT EXISTS MovieDetails(
                      id            INTEGER NOT NULL PRIMARY KEY UNIQUE,
                      movie_name    TEXT UNIQUE,
                      director_id         INTEGER,
                      contRate_id      INTEGER
                );

                  CREATE TABLE IF NOT EXISTS Genres (
                      id            INTEGER NOT NULL PRIMARY KEY UNIQUE,
                      genre_id      INTEGER
                );
                  CREATE TABLE IF NOT EXISTS GenreList (
                      id        INTEGER NOT NULL PRIMARY KEY UNIQUE,
                      genre     TEXT UNIQUE
                );

                  CREATE TABLE IF NOT EXISTS ContentRateList (
                      id        INTEGER NOT NULL PRIMARY KEY UNIQUE,
                      contRate  TEXT UNIQUE
                );

                  CREATE TABLE IF NOT EXISTS DirectorList (
                      id        INTEGER NOT NULL PRIMARY KEY UNIQUE,
                      director  TEXT UNIQUE
                );
                  ''')

base_url = 'http://www.imdb.com'

cur.execute('''
            SELECT movie_id,link FROM MovieLinks ORDER BY movie_id;
            ''')

data = cur.fetchall()

for movie_id, link in data:
    if movie_id >= 3:
        break
    print("Retriving Movie: {}".format(movie_id))
    mv_url = base_url + link
    response = requests.get(mv_url)
    soup = BeautifulSoup(response.text, 'lxml')

    js_script = soup.select('script[type="application/ld+json"]')[0].contents[0]
    js = json.loads(js_script)


    contRate = js['contentRating']
    movie_name = js['name']
    dirc_name = js['director']['name']

    cur.execute('''
                INSERT OR IGNORE INTO ContentRateList (contRate)
                VALUES (?)
                ''', (contRate,))
    cur.execute('''
                SELECT id FROM ContentRateList WHERE contRate=?
                ''', (contRate,))
    contRate_id = cur.fetchone()[0]

    cur.execute('''
                INSERT OR IGNORE INTO DirectorList (director)
                VALUES (?)
                ''', (dirc_name,))
    cur.execute('''
                SELECT id FROM DirectorList WHERE director=?
                ''', (dirc_name,))
    director_id = cur.fetchone()[0]


    cur.execute('''
                INSERT OR IGNORE INTO MovieDetails (movie_name, contRate_id, director_id)
                VALUES (?,?,?)''', (movie_name, contRate_id, director_id))

print("Retrived All Movies!")

conn.commit()
conn.close()
