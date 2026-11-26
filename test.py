import sqlite3 #For the db
import requests #Used to pull from website data and API's (TMDB, MovieLens)
import os 

from pathlib import Path #For Writing to .env
from dotenv import load_dotenv #needed to read the .env

#Initalize the db based on the sql file
def init_db():
    """
    Intalizes the db
    """

    connection = sqlite3.connect("flicks.db")
    connection.execute("PRAGMA foreign_keys = ON")

    flicks_sql = Path("flicks.sql").read_text()
    connection.executescript(flicks_sql)

    connection.close()

    print("Database initialized.")

#Link TMDB command (to api key) store in .env

ENV_PATH = Path(".env")

    #Set the API key from the user into the .env
def set_api_key(api_key: str):
    """
    Writes/Replaces the TMDB api key into the .env without interfering with any other lines.

    For testing:
    >>> from <file name you are in> import set_api_key
    >>> set_api_key("your_key_here")
    """
    lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
    lines = [l for l in lines if not l.startswith("TMDB_API_KEY=")]
    lines.append(f"TMDB_API_KEY={api_key.strip()}")
    ENV_PATH.write_text("\n".join(lines) + "\n")
    print(f"Saved TMDB_API_KEY to {ENV_PATH}")

    #Get the api key from the .env
def get_api_key():
    load_dotenv(ENV_PATH, override=True)
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise ValueError("TMDB API key not found. Please set the API key first.")
    return api_key

#Need a downloader to get the Movielens 32M dataset

#Get Movie Movielends ID

#Get Movie TMDB ID

TMDB_URL = "https://api.themoviedb.org/3"

def get_movie_tmdb_id(title, year=None):
    """
    Search TMDB for a movie based on title and year (optional) and get the TMDB ID
    
    TMDB will also respond with 0 to 20 respones. You cannot limit the count other than
    manually getting the count you want from the results.

    This function can allow a searched item not in the database already to then get pulled into it.

    For testing:
    >>> from <file name you are in> import get_movie_tmdb_id
    >>> get_movie_tmdb_id(,)
    """
    params = {
        "api_key": get_api_key(),
        "query": title,
        "include_adult": False #False excludes any adult content
    }
    if year: #If year param is passed then add it to the params
        params["year"] = year
    
    response = requests.get(
        f"{TMDB_URL}/search/movie",
        params=params
    )
    response.raise_for_status()
    results = response.json()["results"]

    if not results: #If no result is found then print nothing was found.
        print("No movies found.")
        return None

    print("\nSearch results:")

    #Gets the first 10 movie results. for testing purposes
    for i, movie in enumerate(results[:10]):
        print(
            f"{i + 1}. {movie['title']} "
            f"({movie.get('release_date', 'Unknown')})"
        )

    #Returns the ID of the movie
    return results[0]["id"]

#Get Movielends data if any?
#Get TMDB entry data (GET Cast, GET Genres, GET Director, Get Keywords) using TMDB ID

def get_tmdb_entry_data(tmdb_id):
    """
    Uses the TMDB_ID to get the details, genres, keywords, cast, and directors
    """

    params = {
        "api_key": get_api_key(),
        "append_to_response": "credits,keywords"
    }

    response = requests.get( #Send a get request to TMDB with the params
        f"{TMDB_URL}/movie/{tmdb_id}",
        params=params
    )

    response.raise_for_status()

    data = response.json() #Convert the response into a json.

    #Director
    director = next(
        (
            member["name"]
            for member in data.get("credits", {}).get("crew", []) #Gets all the members of the crew from the credits section
            if member["job"] == "Director" #If the crew members job is Director then they are the Director
        ),
        None #If no director is found set None
    )

    #Cast
    cast = [
        member["name"]
        for member in data.get("credits", {}).get("cast", []) #Works the same as the director command but just gets all cast members.
    ]

    # Genres
    genres = [
        genre["name"]
        for genre in data.get("genres", []) #Get all the genres
    ]

    # Keywords
    keywords = [
        keyword["name"]
        for keyword in data.get("keywords", {}).get("keywords", []) #Get all the keywords.
    ]

    return {
        "tmdb_id": data["id"],
        "title": data.get("title"),
        "overview": data.get("overview"),
        "director": director,
        "release_date": data.get("release_date"),
        "runtime": data.get("runtime"),
        "genres": genres,
        "cast": cast,
        "keywords": keywords
    }

# ADD MOVIE TO DATABASE
def add_movie_to_db(db_path, movie):
    """
    Put the movie data into the database.
    """
    #If the db isn't made, make it.
    #Only thing to think of for the future is if the table gets edited somehow it may not be happy with the layout.
    #So potentially check that all tables are present.
    if not Path("flicks.db").exists(): 
        init_db()

    connection = sqlite3.connect(db_path) #Connect to the sql database
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        #Check if movie already exists
        existing = connection.execute(
            "SELECT movie_id FROM Movies WHERE tmdb_id = ?",
            (movie["tmdb_id"],)
        ).fetchone()

        if existing:
            print("Movie already exists in database.")
            return existing[0]

        #Insert movie
        cursor = connection.execute("""
            INSERT INTO Movies (
                tmdb_id,
                title,
                overview,
                director,
                release_date,
                runtime
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            movie["tmdb_id"],
            movie["title"],
            movie["overview"],
            movie["director"],
            movie["release_date"],
            movie["runtime"]
        ))

        movie_id = cursor.lastrowid

        #Insert genres
        for genre in movie["genres"]:

            connection.execute("""
                INSERT OR IGNORE INTO Genres (genre_name)
                VALUES (?)
            """, (genre,))

            genre_id = connection.execute(
                "SELECT genre_id FROM Genres WHERE genre_name = ?",
                (genre,)
            ).fetchone()[0]

            connection.execute("""
                INSERT OR IGNORE INTO MovieGenres
                (movie_id, genre_id)
                VALUES (?, ?)
            """, (movie_id, genre_id))

        #Insert keywords
        for keyword in movie["keywords"]:

            connection.execute("""
                INSERT OR IGNORE INTO Keywords (keyword)
                VALUES (?)
            """, (keyword,))

            keyword_id = connection.execute(
                "SELECT keyword_id FROM Keywords WHERE keyword = ?",
                (keyword,)
            ).fetchone()[0]

            connection.execute("""
                INSERT OR IGNORE INTO MovieKeywords
                (movie_id, keyword_id)
                VALUES (?, ?)
            """, (movie_id, keyword_id))

        #Insert cast
        for actor in movie["cast"]:

            connection.execute("""
                INSERT OR IGNORE INTO Actors (actor_name)
                VALUES (?)
            """, (actor,))

            actor_id = connection.execute(
                "SELECT actor_id FROM Actors WHERE actor_name = ?",
                (actor,)
            ).fetchone()[0]

            connection.execute("""
                INSERT OR IGNORE INTO "Cast"
                (movie_id, actor_id)
                VALUES (?, ?)
            """, (movie_id, actor_id))

        connection.commit()

        print(f"Successfully added {movie['title']}!")
        print(f"Internal Movie ID: {movie_id}")

        return movie_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

#Setup a command to get 1 new movie at a time

def add_one_movie():
    """
    Test command to search for a new movie and then add it to the DB.

    For testing:
    >>> from <file name you are in> import add_one_movie
    >>> add_one_movie()
    """

    title = input("Enter movie title: ").strip()

    year = input("Enter release year (optional): ").strip()

    tmdb_id = get_movie_tmdb_id(
        title,
        int(year) if year else None
    )

    if tmdb_id is None:
        return

    movie = get_tmdb_entry_data(tmdb_id)

    return add_movie_to_db("flicks.db", movie)

#Make a test command that can request the system to get 1 new movie.
#   What is the best system to get a new movie?
#       Base it off of either TMDB most popular?
#       Should we get all the movies from the Movielens 32M first then do TMDB?
#       Could probably add apart of the search bar that any movie searched for but not included gets pulled from TMDB

