# Docker Fundamentals & Best Practices

## Multi-Stage Build (Python)

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
CMD ["python", "app.py"]
```

## Multi-Stage Build (Go)

```dockerfile
FROM golang:1.21-alpine as builder
WORKDIR /app
COPY go.mod go.sum .
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/app .
CMD ["./app"]
```

## Image Optimization

### Size Reduction
```dockerfile
# ❌ Bad (1.2GB)
FROM ubuntu:latest
RUN apt-get update && apt-get install python3

# ✅ Good (150MB)
FROM python:3.11-slim
# Only includes Python and minimal deps
```

### Layer Caching
```dockerfile
# ✅ Good - Dockerfile changes don't invalidate dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# ❌ Bad - Changes to code rebuild dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
```

## Security Best Practices

### Non-root User
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### Read-only Filesystem
```dockerfile
RUN chmod 444 /app/config.yml
```

### No Secrets in Image
```dockerfile
# ❌ Bad
RUN curl -H "Authorization: Bearer $API_KEY" ...

# ✅ Good
# Pass secrets via build args or mount at runtime
```

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

## Environment Variables & Config

```dockerfile
# Development
ENV DATABASE_URL=postgres://localhost/dev

# Override at runtime
docker run -e DATABASE_URL=postgres://prod/db app
```

## Working with Registries

### Build & Push
```bash
# Tag image
docker tag myapp:latest myregistry.azurecr.io/myapp:latest

# Push to registry
docker push myregistry.azurecr.io/myapp:latest

# Pull from registry
docker pull myregistry.azurecr.io/myapp:latest
```

### Private Registry
```bash
docker login myregistry.azurecr.io
docker push myregistry.azurecr.io/myapp:v1.0
```

## Debugging Containers

```bash
# Interactive shell
docker run -it myapp sh

# View logs
docker logs <container_id>

# Inspect running container
docker inspect <container_id>

# Execute command in running container
docker exec -it <container_id> sh
```

## Container Networking

### Bridge Network
```bash
docker network create mynetwork
docker run --network mynetwork --name service1 myapp
docker run --network mynetwork --name service2 myapp
# service1 can reach service2 by name
```

### Port Mapping
```bash
docker run -p 8080:8080 myapp
# Maps host:8080 -> container:8080
```

## Volume Management

```bash
# Named volume
docker run -v mydata:/app/data myapp

# Bind mount
docker run -v $(pwd)/data:/app/data myapp

# Read-only
docker run -v mydata:/app/data:ro myapp
```
