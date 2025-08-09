# 🎬 Movie Recommendation Backend

## 🚀 Real-World Application

This backend project simulates real-world development scenarios where **performance**, **security**, and **user-centric design** are paramount.
It offers hands-on experience with:

- API development and third-party integration
- High-performance caching strategies
- Comprehensive API documentation for seamless frontend collaboration

---

## Overview

This case study centers on building a **robust backend** for a movie recommendation application. It provides RESTful APIs for:

- Fetching trending and recommended movies
- Authenticating users securely
- Saving and retrieving user preferences

The system is optimized for performance and includes detailed documentation to support frontend integration.

---

## Project Goals

- **API Creation**  
  Develop endpoints to serve trending and recommended movies using external APIs.

- **User Management**  
  Implement secure JWT-based authentication and allow users to save favorite movies.

- **Performance Optimization**  
  Use Redis caching to reduce latency and minimize external API calls.

---

## Technologies Used

| Technology | Purpose                       |
| ---------- | ----------------------------- |
| Django     | Backend framework             |
| PostgreSQL | Relational database           |
| Redis      | Caching layer for performance |
| Swagger    | API documentation             |

---

## Key Features

### Movie Recommendation API

- Integrates with third-party movie APIs (e.g., TMDb)
- Serves trending and personalized recommendations
- Includes robust error handling for external API failures

### User Authentication & Preferences

- JWT-based authentication for secure access
- Models for saving and retrieving user favorites

### Performance Optimization

- Redis caching for trending and recommended movies
- Reduces redundant API calls and improves response time

### Comprehensive Documentation

- Swagger-powered API docs hosted at `/api/docs`
- Facilitates smooth frontend integration and testing

---

## Implementation Process

1. **Project Setup**

   - Initialize Django project and configure PostgreSQL and Redis
   - Set up environment variables for third-party API keys

2. **API Development**

   - Create endpoints for trending and recommended movies
   - Integrate TMDb (or similar) API with error handling

3. **Authentication & User Models**

   - Implement JWT authentication
   - Create models for user preferences and favorites

4. **Caching Strategy**

   - Use Redis to cache movie data
   - Set expiration policies to balance freshness and performance

5. **Documentation**
   - Annotate views and serializers with Swagger decorators
   - Host interactive API docs at `/api/docs`

---

---

## Running the Project

```bash
# Clone the repo
git clone git@github.com:bicosteve/movie-recommendation-api.git
cd movie-recommendation-api

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```
