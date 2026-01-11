# Flask REST API

A Restful API built with Flask, featuring JWT authentication, SQLAlchemy ORM, and PostgreSQL database.

## Features

- **JWT Authentication** - Secure user authentication with JWT tokens
- **Store Management** - CRUD operations for stores
- **Item Management** - CRUD operations for items with store relationships
- **Tag System** - Tag items with many-to-many relationships
- **User Management** - User registration and authentication
- **Database Migrations** - Alembic migrations for database schema management

## Project Structure

```
restApi/
├── app.py                 # Main Flask application factory
├── config.py             # Configuration settings
├── db.py                 # Database instance
├── schemas.py            # Marshmallow schemas for validation
├── blocklist.py          # JWT token blocklist
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker build instructions
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── models/               # SQLAlchemy models
│   ├── __init__.py
│   ├── store.py
│   ├── item.py
│   ├── tag.py
│   ├── user.py
│   └── item_tags.py
└── resources/            # API endpoints
    ├── store.py
    ├── item.py
    ├── tag.py
    └── user.py
```

## Prerequisites

- Docker installed on your machine
- Git (to clone the repository)

## Running Locally with Docker Compose

### 1. Clone and Setup

```bash
git clone <repository-url>
cd restApi
```

### 2. Environment Configuration

Make sure your `.env` file contains the correct database URL for local development:

```env
DATABASE_URL=postgresql://postgres:password@db:5432/myapp
```

### 3. Start the Application

Run the following command to start the web application, PostgreSQL database, and RabbitMQ:

```bash
docker compose up --build --force-recreate --no-deps
```

**Command breakdown:**
- `--build`: Rebuilds the Docker images
- `--force-recreate`: Recreates containers even if configuration hasn't changed
- `--no-deps`: Don't start linked services

### 4. Start the Email Worker

In a separate terminal, run the RQ worker for email processing:

```bash
docker run -w /app run-task-test sh -c "rq worker -u <redisUrl> emails"
```

This starts the Redis Queue worker that processes email tasks in the background.

### 5. Access the Application

Once the containers are running:

- **API Base URL**: `http://localhost:5000`
- **Swagger Documentation**: `http://localhost:5000/swagger-ui`
- **Database**: Available on `localhost:5432`
  - Username: `postgres`
  - Password: `password`
  - Database: `myapp`

## API Endpoints

The API provides the following main endpoints:

### Authentication
- `POST /register` - Register a new user
- `POST /login` - Login and get JWT token
- `POST /logout` - Logout (blacklist token)
- `POST /refresh` - Refresh JWT token

### Stores
- `GET /stores` - Get all stores
- `POST /stores` - Create a new store
- `GET /stores/{id}` - Get a specific store
- `PUT /stores/{id}` - Update a store
- `DELETE /stores/{id}` - Delete a store

### Items
- `GET /items` - Get all items
- `POST /items` - Create a new item
- `GET /items/{id}` - Get a specific item
- `PUT /items/{id}` - Update an item
- `DELETE /items/{id}` - Delete an item

### Tags
- `GET /tags` - Get all tags
- `POST /tags` - Create a new tag
- `GET /tags/{id}` - Get a specific tag
- `DELETE /tags/{id}` - Delete a tag
