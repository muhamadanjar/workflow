# Advanced Mermaid Diagrams

Complex patterns. Architecture, mindmaps, timelines, C4.

## 1. Architecture Diagram (System Design)

### Microservices Architecture

```mermaid
graph TB
    Client[Client Apps]
    LB[Load Balancer]
    
    subgraph API Gateway
        GW[API Gateway]
    end
    
    subgraph Services
        Auth[Auth Service]
        User[User Service]
        Order[Order Service]
        Payment[Payment Service]
    end
    
    subgraph Databases
        AuthDB[(Auth DB)]
        UserDB[(User DB)]
        OrderDB[(Order DB)]
    end
    
    subgraph Cache & Queue
        Redis[Redis Cache]
        RabbitMQ[RabbitMQ]
    end
    
    subgraph External
        PaymentGW[Payment Gateway]
        Email[Email Service]
    end
    
    Client --> LB
    LB --> GW
    GW --> Auth
    GW --> User
    GW --> Order
    GW --> Payment
    
    Auth --> AuthDB
    User --> UserDB
    Order --> OrderDB
    
    Auth --> Redis
    User --> Redis
    Order --> RabbitMQ
    
    Payment --> PaymentGW
    RabbitMQ --> Email
```

### Web Application Stack

```mermaid
graph TD
    Client[Browser/Mobile]
    CDN[CDN]
    
    subgraph Frontend
        SPA[React/Vue App]
        Router[Router]
    end
    
    subgraph Backend
        LB[Load Balancer]
        API1[API Server 1]
        API2[API Server 2]
        API3[API Server 3]
    end
    
    subgraph Data
        PrimaryDB[(PostgreSQL Primary)]
        ReplicaDB[(Replica)]
        Cache[Redis Cache]
    end
    
    subgraph Background
        Worker1[Background Worker 1]
        Worker2[Background Worker 2]
        Queue[Job Queue]
    end
    
    Client --> CDN
    Client --> SPA
    SPA --> Router
    Router --> LB
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> Cache
    API2 --> Cache
    API3 --> Cache
    
    API1 --> PrimaryDB
    API2 --> PrimaryDB
    API3 --> PrimaryDB
    
    PrimaryDB --> ReplicaDB
    
    API1 --> Queue
    API2 --> Queue
    
    Queue --> Worker1
    Queue --> Worker2
    
    Worker1 --> Cache
    Worker2 --> Cache
```

## 2. Mindmap

### Project Planning

```mermaid
mindmap
  root((Project))
    Planning
      Requirements
        Functional
        Non-Functional
      Design
        Architecture
        Database
        UI/UX
    Development
      Frontend
        Components
        State Management
        Styling
      Backend
        API Design
        Database
        Authentication
      DevOps
        Docker
        CI/CD
        Deployment
    Testing
      Unit Tests
      Integration Tests
      E2E Tests
    Deployment
      Staging
      Production
      Monitoring
```

### Product Roadmap

```mermaid
mindmap
  root((Product))
    Phase 1: MVP
      Core Features
        User Auth
        Create Post
        View Feed
      Database Schema
      Basic UI
    Phase 2: Growth
      Advanced Features
        Comments
        Likes
        Follow System
      Performance
        Caching
        Optimization
    Phase 3: Scale
      Infrastructure
        Microservices
        Load Balancing
        Database Sharding
      Analytics
        User Tracking
        Metrics
```

## 3. Timeline

### Release Timeline

```mermaid
timeline
    title Project Timeline
    2024-01 : Planning : Requirements Gathering
    2024-02 : Design : Architecture & Mockups
    2024-03 : Development : API & Frontend
    2024-04 : Testing : QA & Bug Fixes
    2024-05 : Deployment : Beta Release
    2024-06 : Launch : Production Release
    2024-07 : Monitoring : Performance Tuning
```

### Sprint Schedule

```mermaid
timeline
    title Sprint Schedule
    Sprint 1 : Setup : Development Environment
    Sprint 1 : : Project Structure
    Sprint 2 : API : Authentication Endpoints
    Sprint 2 : : User Management
    Sprint 3 : Frontend : Login/Register Pages
    Sprint 3 : : Dashboard Layout
    Sprint 4 : Testing : Unit Tests
    Sprint 4 : : Integration Tests
```

## 4. Git Graph

### Git Workflow (Feature Branch)

```mermaid
gitGraph
    commit id: "Initial"
    commit id: "Setup Project"
    
    branch develop
    checkout develop
    commit id: "Add config"
    commit id: "Add models"
    
    branch feature/auth
    checkout feature/auth
    commit id: "Auth controller"
    commit id: "Auth service"
    commit id: "Auth tests"
    
    checkout develop
    merge feature/auth
    commit id: "Update docs"
    
    branch feature/api
    checkout feature/api
    commit id: "API routes"
    commit id: "Validation"
    
    checkout develop
    merge feature/api
    commit id: "v1.0.0"
    
    checkout main
    merge develop
    commit id: "Release v1.0.0"
```

## 5. Pie Chart

### Market Share

```mermaid
pie title Market Share 2024
    "Chrome" : 65
    "Firefox" : 15
    "Safari" : 12
    "Edge" : 8
```

### Project Time Allocation

```mermaid
pie title Development Time
    "Feature Dev" : 40
    "Testing" : 25
    "Bug Fixes" : 20
    "Documentation" : 10
    "Meetings" : 5
```

## 6. Gantt Chart (Advanced)

### Project Timeline

```mermaid
gantt
    title Project Gantt
    dateFormat YYYY-MM-DD
    
    section Planning
    Requirements :req, 2024-01-01, 30d
    Design :des, 2024-01-15, 20d
    
    section Development
    Backend :backend, 2024-02-01, 45d
    Frontend :frontend, 2024-02-15, 40d
    Database :db, 2024-02-01, 30d
    
    section Testing
    Unit Tests :test1, 2024-03-15, 20d
    Integration :test2, 2024-03-25, 20d
    E2E :test3, 2024-04-05, 15d
    
    section Deployment
    Staging :stage, 2024-04-20, 10d
    Production :prod, 2024-04-30, 1d
```

## 7. C4 Context Diagram

### System Context

```mermaid
graph TB
    User[User]
    System[E-Commerce System]
    Payment[Payment Provider]
    Email[Email Service]
    
    User -->|Uses| System
    System -->|Processes Payments| Payment
    System -->|Sends Emails| Email
```

### Container Diagram

```mermaid
graph TB
    User[User]
    Browser[Web Browser]
    API[API Server]
    DB[(Database)]
    Cache[Cache]
    
    User -->|Uses| Browser
    Browser -->|HTTP/REST| API
    API -->|Read/Write| DB
    API -->|Cache| Cache
```

## 8. Complex State Machine

### Order Processing State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending
    
    Pending --> PaymentProcessing: Process Payment
    PaymentProcessing --> PendingConfirmation: Payment Successful
    PaymentProcessing --> Cancelled: Payment Failed
    
    PendingConfirmation --> Processing: Confirm Order
    PendingConfirmation --> Pending: Edit Order
    
    Processing --> ReadyToShip: Pick & Pack
    ReadyToShip --> Shipped: Ship
    Shipped --> Delivered: Deliver
    
    Processing --> OnHold: Stock Issue
    OnHold --> Processing: Stock Available
    OnHold --> Cancelled: Cancelled
    
    Delivered --> [*]
    Cancelled --> [*]
```

## Patterns

### System Integration Pattern

```mermaid
graph TB
    subgraph Source
        SourceDB[(Source DB)]
    end
    
    subgraph Integration
        ETL[ETL Pipeline]
        Queue[Message Queue]
        Cache[Cache Layer]
    end
    
    subgraph Target
        TargetDB[(Target DB)]
        API[API]
    end
    
    SourceDB --> ETL
    ETL --> Queue
    Queue --> Cache
    Cache --> TargetDB
    Cache --> API
```

### Event-Driven Architecture

```mermaid
graph TB
    Producer[Event Producer]
    Broker[Message Broker]
    
    Consumer1[Consumer 1]
    Consumer2[Consumer 2]
    Consumer3[Consumer 3]
    
    DB1[(DB 1)]
    DB2[(DB 2)]
    Service3[Service 3]
    
    Producer -->|Event| Broker
    Broker -->|Event| Consumer1
    Broker -->|Event| Consumer2
    Broker -->|Event| Consumer3
    
    Consumer1 --> DB1
    Consumer2 --> DB2
    Consumer3 --> Service3
```

## Best Practices for Advanced Diagrams

1. **Use Subgraphs** — Group related components
2. **Color Code** — Distinguish layers/services
3. **Label Arrows** — Explain relationships
4. **Keep Balanced** — Avoid crowding
5. **Document Purpose** — Add titles/descriptions
6. **Version Control** — Track diagram changes
7. **Test Rendering** — Preview before sharing

## Performance Tips

- **Large diagrams** — Break into multiple diagrams
- **Many nodes** — Use zoom-friendly SVG format
- **Complex flows** — Consider splitting into sections
- **Readable** — Use 12pt+ font size in rendering

## Tools for Rendering

```bash
# Render with high quality
mmdc -i diagram.mmd -o diagram.png -s 2

# Render to SVG (vector, better for presentations)
mmdc -i diagram.mmd -o diagram.svg

# Render with custom config
mmdc -i diagram.mmd -o diagram.png -c config.json
```

---

**See [BEST_PRACTICES.md](BEST_PRACTICES.md) for optimization and styling.**
