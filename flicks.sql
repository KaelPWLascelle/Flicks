CREATE TABLE Movies (
    movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
    movielens_id INTEGER UNIQUE,
    tmdb_id INTEGER UNIQUE,
    title TEXT,
    overview TEXT,
    director TEXT,
    release_date TEXT,
    runtime INTEGER
);

CREATE TABLE Genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name TEXT UNIQUE
);

CREATE TABLE MovieGenres (
    movie_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE Keywords (
    keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL UNIQUE
);

CREATE TABLE MovieKeywords (
    movie_id INTEGER,
    keyword_id INTEGER,
    PRIMARY KEY (movie_id, keyword_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id),
    FOREIGN KEY (keyword_id) REFERENCES Keywords(keyword_id)
);

CREATE TABLE Actors (
    actor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_name TEXT UNIQUE
);

CREATE TABLE Cast (
    movie_id INTEGER,
    actor_id INTEGER,
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id),
    FOREIGN KEY (actor_id) REFERENCES Actors(actor_id)
);

CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    created TEXT
);

CREATE TABLE UserRatings (
    user_id INTEGER,
    movie_id INTEGER,
    watched INTEGER,
    rating REAL,
    timestamp TEXT,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
);

CREATE TABLE MovieFeatures (
    movie_id INTEGER PRIMARY KEY,
    feature_vector TEXT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
);

CREATE TABLE FeatureDefinitions (
    feature_id INTEGER PRIMARY KEY,
    feature_name TEXT UNIQUE NOT NULL
);