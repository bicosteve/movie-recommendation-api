CREATE TABLE movies(
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    overview TEXT NOT NULL, 
    genres TEXT NOT NULL, 
    release_date DATE NOT NULL, 
    poster_url VARCHAR(1025) NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_movies_id ON movies(id);