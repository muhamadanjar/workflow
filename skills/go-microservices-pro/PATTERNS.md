# Go Microservices Patterns

## Circuit Breaker

```go
type CircuitBreaker struct {
    maxFailures int
    timeout     time.Duration
    state       string // "closed", "open", "half-open"
    failures    int
}

func (cb *CircuitBreaker) Call(fn func() error) error {
    if cb.state == "open" {
        return errors.New("circuit breaker open")
    }
    
    err := fn()
    if err != nil {
        cb.failures++
        if cb.failures >= cb.maxFailures {
            cb.state = "open"
        }
    } else {
        cb.failures = 0
        cb.state = "closed"
    }
    return err
}
```

## Retry with Exponential Backoff

```go
func RetryWithBackoff(maxAttempts int, fn func() error) error {
    var err error
    for attempt := 0; attempt < maxAttempts; attempt++ {
        err = fn()
        if err == nil {
            return nil
        }
        
        backoff := time.Duration(math.Pow(2, float64(attempt))) * time.Second
        time.Sleep(backoff)
    }
    return err
}
```

## Bulkhead Pattern (Concurrency Limiting)

```go
type Bulkhead struct {
    semaphore chan struct{}
}

func NewBulkhead(maxConcurrent int) *Bulkhead {
    return &Bulkhead{
        semaphore: make(chan struct{}, maxConcurrent),
    }
}

func (b *Bulkhead) Execute(fn func() error) error {
    b.semaphore <- struct{}{}
    defer func() { <-b.semaphore }()
    return fn()
}
```

## Saga Pattern (Distributed Transactions)

```go
type Saga struct {
    steps []Step
}

type Step struct {
    action   func() error
    rollback func() error
}

func (s *Saga) Execute() error {
    executed := []Step{}
    
    for _, step := range s.steps {
        if err := step.action(); err != nil {
            // Rollback in reverse
            for i := len(executed) - 1; i >= 0; i-- {
                executed[i].rollback()
            }
            return err
        }
        executed = append(executed, step)
    }
    return nil
}
```

## Event Sourcing

```go
type Event struct {
    Type      string
    Timestamp time.Time
    Data      interface{}
}

type EventStore interface {
    Append(ctx context.Context, aggregateID string, event Event) error
    GetEvents(ctx context.Context, aggregateID string) ([]Event, error)
}

func ReplayEvents(events []Event, aggregate interface{}) error {
    for _, event := range events {
        // Apply each event to rebuild state
    }
    return nil
}
```

## CQRS (Command Query Responsibility Segregation)

```go
// Commands modify state
type CreateUserCommand struct {
    Name  string
    Email string
}

// Queries read state
type GetUserQuery struct {
    UserID string
}

// Separate handlers
type CommandHandler interface {
    Handle(ctx context.Context, cmd CreateUserCommand) error
}

type QueryHandler interface {
    Handle(ctx context.Context, query GetUserQuery) (*User, error)
}
```

## Service Mesh Patterns

### Service Discovery
- Consul
- Eureka
- Kubernetes DNS

### Load Balancing
- Client-side (gRPC)
- Server-side (Nginx, HAProxy)

### Health Checking
```go
func HealthCheck(w http.ResponseWriter, r *http.Request) {
    if isHealthy() {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("ok"))
    } else {
        w.WriteHeader(http.StatusServiceUnavailable)
    }
}
```

## Anti-Patterns to Avoid

- ❌ Synchronous communication everywhere
- ❌ Shared databases between services
- ❌ No circuit breakers for external calls
- ❌ Ignoring network latency
- ❌ Hard-coded service addresses
- ❌ No timeouts on requests
