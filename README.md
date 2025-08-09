# Movie Recommendation Backend

## Real-World Application

This backend system replicates real-world engineering scenarios where performance, security, and API clarity are paramount. By completing this project, I have gained proficiency in:

- Building and documenting scalable APIs
- Implementing Redis-based caching strategies
- Designing secure authentication workflows

---

## Overview

This Django-powered backend serves a movie recommendation platform, offering APIs for:

- Trending and recommended movie retrieval
- User authentication (JWT)
- Saving favorite movie preferences

It prioritizes performance optimization through caching and follows documentation best practices via Swagger.

---

## Project Goals

- **API Development**: Provide endpoints for movie listing and user actions
- **Authentication**: Implement JWT authentication and user preference saving
- **Performance**: Leverage Redis to cache frequent movie queries

---

## Technologies Used

| Technology | Purpose                          |
| ---------- | -------------------------------- |
| Django     | Core backend framework           |
| PostgreSQL | Persistent relational datastore  |
| Redis      | Caching for trending/recommended |
| Swagger    | API documentation interface      |

---

## Key Features

### Movie API Integration

- Connects to TMDb for trending and recommended movies
- Implements error resilience with retry strategies and fallbacks

### User Authentication & Preferences

- JWT-based login/signup
- Users can save and retrieve favorite movies

### Performance Optimization

- Redis cache for movie data (e.g., `/api/movies/trending`)
- Reduces third-party API load and improves response latency

### Comprehensive API Docs

- Swagger integrated via `drf-yasg`
- Live docs hosted at: `/api/docs`
