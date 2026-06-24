# Production Readiness for Go Microservices

## Observability Stack

### Structured Logging
```go
import "go.uber.org/zap"

logger, _ := zap.NewProduction()
logger.Info("user created", 
    zap.String("user_id", "123"),
    zap.String("email", "user@example.com"),
)
```

### Distributed Tracing
```go
import "go.opentelemetry.io/otel"
import "go.opentelemetry.io/otel/exporters/jaeger"

tracer := otel.Tracer("user-service")
ctx, span := tracer.Start(context.Background(), "GetUser")
defer span.End()
```

### Metrics
```go
import "github.com/prometheus/client_golang/prometheus"

requestCounter := prometheus.NewCounterVec(
    prometheus.CounterOpts{Name: "http_requests_total"},
    []string{"method", "endpoint"},
)

requestCounter.WithLabelValues("GET", "/users").Inc()
```

## Health Checks

```go
type HealthStatus struct {
    Status   string            `json:"status"`
    Services map[string]string `json:"services"`
}

func HealthCheck(repos *Repositories) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        status := HealthStatus{
            Status:   "healthy",
            Services: make(map[string]string),
        }
        
        // Check database
        if err := repos.Ping(); err != nil {
            status.Services["database"] = "unhealthy"
            status.Status = "unhealthy"
        } else {
            status.Services["database"] = "healthy"
        }
        
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(status)
    }
}
```

## Rate Limiting

```go
import "golang.org/x/time/rate"

limiter := rate.NewLimiter(100, 10) // 100 req/s, burst 10

func rateLimitMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if !limiter.Allow() {
            http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

## Request/Response Validation

```go
type CreateUserRequest struct {
    Name  string `json:"name" validate:"required,min=2"`
    Email string `json:"email" validate:"required,email"`
}

func validateRequest(req *CreateUserRequest) error {
    validate := validator.New()
    return validate.Struct(req)
}
```

## Database Connection Pooling

```go
db, err := sql.Open("postgres", dsn)
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(5)
db.SetConnMaxLifetime(5 * time.Minute)
```

## Graceful Shutdown

```go
srv := &http.Server{Addr: ":8080"}

go func() {
    if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
        log.Fatal(err)
    }
}()

quit := make(chan os.Signal, 1)
signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
<-quit

ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

if err := srv.Shutdown(ctx); err != nil {
    log.Fatal(err)
}
```

## Deployment Checklist

- [ ] Structured logging configured
- [ ] Metrics exposed on /metrics
- [ ] Health check endpoint working
- [ ] Graceful shutdown implemented
- [ ] Connection pooling optimized
- [ ] Rate limiting configured
- [ ] Circuit breakers in place
- [ ] Timeout values set
- [ ] Error handling complete
- [ ] Request validation added
- [ ] Distributed tracing setup
- [ ] Security headers added
- [ ] CORS properly configured
- [ ] Database migrations versioned
- [ ] Secrets not in code

## Environment Variables

```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=postgres
DB_PASSWORD=secret

# Service
SERVICE_PORT=8080
SERVICE_ENV=production
LOG_LEVEL=info

# External
REDIS_URL=redis://localhost:6379
API_KEY=xxx
```
