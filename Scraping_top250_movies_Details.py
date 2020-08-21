
import sqlite3
import json

conn = sqlite3.connect('IMDB_top_250.sqlite')
cur = conn.cursor()

cur.executescript('''
                  DROP TABLE IF EXISTS ContentRateList;
                  DROP TABLE IF EXISTS MovieDetails;
                  DROP TABLE IF EXISTS DirectorList;
                  DROP TABLE IF EXISTS Directors;
                  DROP TABLE IF EXISTS Genres;
                  DROP TABLE IF EXISTS GenreList;

                  CREATE TABLE IF NOT EXISTS MovieDetails(
                      id                INTEGER NOT NULL PRIMARY KEY UNIQUE,
                      movie_name        TEXT UNIQUE,
                      contRate_id       INTEGER
                );
                /* Genre Moive many-to-many relationship */
                  CREATE TABLE IF NOT EXISTS Genres (
                      movie_id      INTEGER,
                      genre_id      INTEGER,
                      PRIMARY KEY   (movie_id, genre_id)
                );
                  CREATE TABLE IF NOT EXISTS GenreList (
                      id        INTEGER NOT NULL PRIMARY KEY UNIQUE,
                      genre     TEXT UNIQUE
                );

                  CREATE TABLE IF NOT EXISTS ContentRateList (
                      id        INTEGER NOT NULL PRIMARY KEY UNIQUE,
                      contRate  TEXT UNIQUE
                );
                /* Director Movie many-to-many relationship */
                  CREATE TABLE IF NOT EXISTS Directors (
                      movie_id      INTEGER,
                      director_id   INTEGER,
                      PRIMARY KEY   (movie_id, director_id)
                );
                  CREATE TABLE IF NOT EXISTS DirectorList (
                      id        INTEGER NOT NULL PRIMARY KEY UNIQUE,
                      director  TEXT UNIQUE
                );
                  ''')


cur.execute('''
            SELECT movie_id, json_script FROM MovieLinks ORDER BY movie_id;
            ''')
data = cur.fetchall()

def Dir_input(d, movie_id):
        cur.execute('''
                    INSERT OR IGNORE INTO DirectorList (director)
                    VALUES (?)
                    ''', (d['name'],))
        cur.execute('''
                    SELECT id FROM DirectorList WHERE director=?
                    ''', (d['name'],))
        director_id = cur.fetchone()[0]

        cur.execute('''INSERT OR REPLACE INTO Directors (movie_id, director_id)
                    VALUES (?,?)''', (movie_id,director_id))

def Dir_list(dirc, movie_id):
    if type(dirc) is list:
        for d in dirc:
            Dir_input(d, movie_id)
    else:
        Dir_input(dirc, movie_id)


def Genre_input(genre, movie_id):
    cur.execute('''
                INSERT OR IGNORE INTO GenreList (genre)
                VALUES (?)''', (genre,))
    cur.execute('''
                SELECT id FROM GenreList WHERE genre=?
                ''', (genre,))
    genre_id = cur.fetchone()[0]

    cur.execute('''
                INSERT OR REPLACE INTO Genres (movie_id, genre_id)
                VALUES (?,?)
                ''', (movie_id, genre_id))

def Genre_list(g, movie_id):
    if type(g) is list:
        for genre in g:
            Genre_input(genre, movie_id)
    else:
        Genre_input(g, movie_id)


for movie_id, script in data:

    js = json.loads(script)

    try:
        contRate = js['contentRating']
    except:
        contRate = 'Not Rated'

    movie_name = js['name']

    cur.execute('''
                INSERT OR IGNORE INTO ContentRateList (contRate)
                VALUES (?)
                ''', (contRate,))
    cur.execute('''
                SELECT id FROM ContentRateList WHERE contRate=?
                ''', (contRate,))
    contRate_id = cur.fetchone()[0]

    Dir_list(js['director'], movie_id)

    Genre_list(js['genre'], movie_id)

    cur.execute('''
                INSERT OR IGNORE INTO MovieDetails (movie_name, contRate_id)
                VALUES (?,?)''', (movie_name, contRate_id))

print("Database Updated!")

conn.commit()
conn.close()
