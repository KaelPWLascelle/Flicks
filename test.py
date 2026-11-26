import sqlite3

connection = sqlite3.connect("flicks.db")

with open("flicks.sql", "r") as file:
    connection.executescript(file.read())
    
connection.commit()
connection.close()


#Link TMDB command (to api key) store in .env
#Need a downloader to get the Movielens 32M dataset
#Get Movie Movielends ID
#Get Movie TMDB ID
#Get Movielends data if any?
#Get TMDB entry data (GET Cast, GET Genres, GET Director, Get Keywords)
#Setup a command to get 1 new movie at a time
#Make a test command that can request the system to get 1 new movie.
#   What is the best system to get a new movie?
#       Base it off of either TMDB most popular?
#       Should we get all the movies from the Movielens 32M first then do TMDB?
#       Could probably add apart of the search bar that any movie searched for but not included gets pulled from TMDB