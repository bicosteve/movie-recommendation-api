CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL, 
    email VARCHAR(255) UNIQUE NOT NULL, 
    hashed_password VARCHAR(255) NOT NULL, 
    is_verified SMALLINT DEFAULT 0 NOT NULL CHECK(is_verified IN (0,1)),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE UNIQUE INDEX idx_user_id ON users(id);

CREATE UNIQUE INDEX idx_user_email ON users(email);

CREATE UNIQUE INDEX idx_user_usename ON users(username);