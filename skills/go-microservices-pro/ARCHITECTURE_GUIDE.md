# Go Microservices Architecture Guide

## Service Design

### Layered Architecture
```
┌─────────────────┐
│   Transport     │ HTTP, gRPC handlers
├─────────────────┤
│   Business      │ Domain logic, usecases
├─────────────────┤
│   Data          │ Repository pattern
├─────────────────┤
│   External      │ Third-party APIs
└─────────────────┘
```

### Repository Pattern
```go
type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
    Delete(ctx context.Context, id string) error
}

type userRepo struct {
    db *sql.DB
}
```

### Dependency Injection
```go
// Wire dependencies at startup
service := NewUserService(
    userRepo,
    cacheClient,
    logger,
)

handler := NewUserHandler(service)
```

## Service Communication

### gRPC (Internal)
- Strongly typed
- Binary protocol (fast)
- Bidirectional streaming
- Use for service-to-service

### REST (External)
- JSON over HTTP
- Human readable
- Stateless
- Use for public APIs

### Message Queue (Async)
- Decoupled communication
- Retry logic
- Dead letter queues
- Event broadcasting

## Error Handling Strategy

### Define Custom Errors
```go
type ErrNotFound struct {
    ID string
}

func (e *ErrNotFound) Error() string {
    return fmt.Sprintf("resource %s not found", e.ID)
}
```

### Wrap Errors with Context
```go
if err != nil {
    return fmt.Errorf("failed to fetch user: %w", err)
}
```

### Map to HTTP Status
```go
switch err.(type) {
case *ErrNotFound:
    return http.StatusNotFound
case *ErrUnauthorized:
    return http.StatusUnauthorized
default:
    return http.StatusInternalServerError
}
```

## Middleware & Interceptors

### HTTP Middleware
```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        log.Printf("%s %s", r.Method, r.URL)
        next.ServeHTTP(w, r)
    })
}
```

### gRPC Interceptors
```go
func loggingInterceptor(ctx context.Context, req interface{}, 
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    log.Printf("Calling %s", info.FullMethod)
    return handler(ctx, req)
}
```

## Configuration Management

### Environment-based
```go
type Config struct {
    DBHost   string
    DBPort   int
    RedisURL string
    LogLevel string
}

func LoadConfig() *Config {
    return &Config{
        DBHost:   os.Getenv("DB_HOST"),
        DBPort:   parseInt(os.Getenv("DB_PORT")),
        // ...
    }
}
```

### Validation
```go
func (c *Config) Validate() error {
    if c.DBHost == "" {
        return errors.New("DB_HOST required")
    }
    return nil
}
```

## Graceful Shutdown

```go
sigChan := make(chan os.Signal, 1)
signal.Notify(sigChan, syscall.SIGTERM, syscall.SIGINT)

go func() {
    <-sigChan
    // Close connections
    server.GracefulStop()
    db.Close()
}()
```
