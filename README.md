# Smart Airport Pooling Backend

This is a production-ready Django backend for the Smart Airport Ride project.

## Tech Stack
- Django 4.2+
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Swagger (drf-yasg)

## Project Structure
```
smart_airport_pooling/
    config/           # Project settings and configuration
        settings/     # Multi-environment settings
    apps/             # Main application modules
        users/        # User management
        rides/        # Ride management
        pooling/      # Pooling logic
        pricing/      # Dynamic pricing
        core/         # Core/Common utilities
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Copy `.env.example` to `.env` and update the values.
   ```bash
   cp .env.example .env
   ```

3. **Database Setup**
   Ensure PostgreSQL and Redis are running. You can use Docker:
   ```bash
   docker-compose up -d db redis
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Run the Server**
   ```bash
   python manage.py runserver
   ```

## API Documentation
Once the server is running, visit:
- Swagger: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- ReDoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

## Celery
To run the celery worker:
```bash
celery -A config worker -l info
```
