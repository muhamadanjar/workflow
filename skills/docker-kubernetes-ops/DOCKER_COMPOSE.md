# Docker Compose for Local Development

## Basic Setup (Python/FastAPI + PostgreSQL + Redis)

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/myapp
      REDIS_URL: redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Full Stack Example (React + Go + PostgreSQL + Redis)

```yaml
version: '3.8'

services:
  # Frontend
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8080
    depends_on:
      - api
    volumes:
      - ./web:/app
      - /app/node_modules

  # Backend API
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      DATABASE_URL: postgres://postgres:password@db:5432/myapp
      REDIS_URL: redis://cache:6379
      SERVICE_PORT: 8080
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - ./api:/app

  # gRPC Service
  grpc-service:
    build:
      context: ./grpc-service
      dockerfile: Dockerfile
    ports:
      - "50051:50051"
    environment:
      DATABASE_URL: postgres://postgres:password@db:5432/myapp
    depends_on:
      - db

  # Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Cache
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Message Queue
  queue:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: password
    volumes:
      - queue_data:/var/lib/rabbitmq

volumes:
  postgres_data:
  redis_data:
  queue_data:

networks:
  default:
    name: myapp_network
```

## Common Operations

### Start Services
```bash
docker-compose up -d
docker-compose up -d --build  # Rebuild images
```

### View Logs
```bash
docker-compose logs -f api
docker-compose logs -f db --tail=100
```

### Stop Services
```bash
docker-compose down
docker-compose down -v  # Remove volumes too
```

### Run Commands in Services
```bash
# Database migrations
docker-compose exec api python -m alembic upgrade head

# Database shell
docker-compose exec db psql -U postgres -d myapp

# Interactive shell
docker-compose exec api sh
```

### Rebuild Single Service
```bash
docker-compose up -d --build api
```

## Environment Management

### .env File
```bash
# .env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=devpassword
DATABASE_URL=postgresql://postgres:devpassword@db:5432/myapp
REDIS_URL=redis://cache:6379
```

### Reference in Compose
```yaml
environment:
  DATABASE_URL: ${DATABASE_URL}
  REDIS_URL: ${REDIS_URL}
```

## Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 40s
```

## Networking

```yaml
services:
  api:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend

networks:
  frontend:
  backend:
```

### Service Discovery
```bash
# API can reach database using hostname "db"
curl http://db:5432

# Database from API container
DATABASE_URL=postgresql://db:5432/myapp
```
