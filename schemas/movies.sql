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


INSERT INTO 
    movies(tmdb_id,title,overview,genres,release_date,poster_url)
VALUES
    (755898,'War of the Worlds','Will Radford is a top cyber-security.','878.53','2025-07-29','https://image.tmdb.org/t/p/original/8J6UlIFcU7eZfq9iCLbgc8Auklg.jpg'),
    (1087192,'How to Train Your Dragon','On the rugged isle of Berk, where Vikings.','14.10751.28','2025-06-06','https://image.tmdb.org/t/p/original'),
    (1087192,'How to Train Your Dragon','On the rugged isle of Berk, where Vikings.','14.10751.28','2025-06-06','https://image.tmdb.org/t/p/original'),
    (1311031,'Something Japanese','As the Demon Slayer Corps members and Hashira engaged in.','16.28.14.53','2025-07-18','https://image.tmdb.org/t/p/original/8J6UlIFcU7eZfq9iCLbgc8Auklg.jpg'),
    (986206,'Night Carnage','A blogger who is also a werewolf meets a dashing playboy.','28.27.10749','2025-07-29','https://image.tmdb.org/t/p/original/8J6UlIFcU7eZfq9iCLbgc8Auklg.jpg');