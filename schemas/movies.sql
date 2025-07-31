CREATE TABLE movies(
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    overview TEXT NOT NULL, 
    genres TEXT NOT NULL, 
    release_date DATE, 
    poster_url TEXT, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);