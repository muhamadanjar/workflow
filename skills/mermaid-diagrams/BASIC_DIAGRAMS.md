# Basic Mermaid Diagrams

Start here. Flowcharts, sequences, and classes. Copy-paste examples.

## 1. Flowcharts

### Simple Linear Flow

```mermaid
flowchart LR
    A[Start] --> B[Process] --> C[End]
```

### Decision Tree

```mermaid
flowchart TD
    A[User] --> B{Authenticated?}
    B -->|Yes| C[Dashboard]
    B -->|No| D[Login]
    D --> C
```

### Process with Loop

```mermaid
flowchart TD
    A[Start] --> B[Read Item]
    B --> C{More Items?}
    C -->|Yes| D[Process]
    D --> B
    C -->|No| E[End]
```

### API Request Flow

```mermaid
flowchart TD
    A[Client] -->|Request| B[API]
    B -->|Validate| C{Valid?}
    C -->|No| D[Error 400]
    C -->|Yes| E[Database]
    E -->|Query| F{Found?}
    F -->|Yes| G[Response 200]
    F -->|No| H[Error 404]
    D --> I[Return]
    G --> I
    H --> I
```

### Authentication Flow

```mermaid
flowchart TD
    A[User] --> B[Enter Email]
    B --> C[Enter Password]
    C --> D{Valid?}
    D -->|No| E[Show Error]
    E --> B
    D -->|Yes| F{2FA Enabled?}
    F -->|Yes| G[Send Code]
    F -->|No| H[Create Session]
    G --> I[User Enters Code]
    I --> J{Code Valid?}
    J -->|No| K[Retry]
    J -->|Yes| H
    H --> L[Redirect to Dashboard]
```

### Node Types

```mermaid
flowchart TD
    A[Rectangle]
    B(Rounded)
    C{Diamond}
    D[[Subroutine]]
    E[(Database)]
    F[/Input\]
    G[\Output/]
    H((Circle))
```

## 2. Sequence Diagrams

### Simple Request-Response

```mermaid
sequenceDiagram
    Client->>Server: Request
    Server->>Database: Query
    Database-->>Server: Result
    Server-->>Client: Response
```

### Multiple Actors

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Database
    
    User->>Frontend: Click Button
    Frontend->>Backend: API Request
    Backend->>Database: Query
    Database-->>Backend: Data
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Data
```

### Authentication Sequence

```mermaid
sequenceDiagram
    actor User
    participant App as Web App
    participant Server as API Server
    participant Auth as Auth Service
    
    User->>App: Click Login
    App->>Server: POST /auth/login
    Server->>Auth: Verify Credentials
    Auth-->>Server: Token
    Server-->>App: {token, user}
    App->>App: Store Token
    App-->>User: Redirect to Dashboard
```

### Payment Processing

```mermaid
sequenceDiagram
    participant User
    participant Shop
    participant Payment
    participant Bank
    
    User->>Shop: Checkout
    Shop->>Payment: Create Payment
    Payment->>Bank: Verify Card
    Bank-->>Payment: OK
    Payment-->>Shop: Payment ID
    Shop->>Shop: Create Order
    Shop-->>User: Confirmation
```

### Parallel Processing

```mermaid
sequenceDiagram
    participant API
    participant Service A
    participant Service B
    participant Service C
    
    API->>Service A: Task A
    API->>Service B: Task B
    API->>Service C: Task C
    
    par Processing
        Service A->>Service A: Work
        Service B->>Service B: Work
        Service C->>Service C: Work
    end
    
    Service A-->>API: Result A
    Service B-->>API: Result B
    Service C-->>API: Result C
```

## 3. Class Diagrams

### User Class

```mermaid
classDiagram
    class User {
        id: string
        email: string
        password: string
        created_at: datetime
        +register(email, password)
        +login(email, password)
        +logout()
    }
```

### Database Models

```mermaid
classDiagram
    class User {
        id: int
        email: string
        password_hash: string
    }
    
    class Post {
        id: int
        title: string
        content: string
        user_id: int
        created_at: datetime
    }
    
    class Comment {
        id: int
        text: string
        post_id: int
        user_id: int
    }
    
    User "1" --> "*" Post : creates
    User "1" --> "*" Comment : writes
    Post "1" --> "*" Comment : has
```

### E-commerce System

```mermaid
classDiagram
    class Product {
        id: int
        name: string
        price: float
        stock: int
        +getPrice()
        +updateStock()
    }
    
    class Order {
        id: int
        user_id: int
        total: float
        status: string
        +create()
        +cancel()
    }
    
    class OrderItem {
        id: int
        order_id: int
        product_id: int
        quantity: int
        price: float
    }
    
    class User {
        id: int
        name: string
        email: string
        +placeOrder()
    }
    
    Order "1" --> "*" OrderItem : contains
    OrderItem "1" --> "1" Product : references
    User "1" --> "*" Order : places
```

### Inheritance Hierarchy

```mermaid
classDiagram
    class Animal {
        +eat()
        +sleep()
    }
    
    class Mammal {
        +feedBaby()
    }
    
    class Bird {
        +fly()
    }
    
    class Dog {
        +bark()
    }
    
    class Cat {
        +meow()
    }
    
    Animal <|-- Mammal : extends
    Animal <|-- Bird : extends
    Mammal <|-- Dog : extends
    Mammal <|-- Cat : extends
```

## 4. State Diagrams

### Simple State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running: Start
    Running --> Paused: Pause
    Paused --> Running: Resume
    Running --> Stopped: Stop
    Paused --> Stopped: Stop
    Stopped --> [*]
```

### User Authentication States

```mermaid
stateDiagram-v2
    [*] --> LoggedOut
    LoggedOut --> EnteringEmail: User Input
    EnteringEmail --> EnteringPassword: Next
    EnteringPassword --> Authenticating: Submit
    Authenticating --> LoggedIn: Success
    Authenticating --> EnteringPassword: Fail
    LoggedIn --> LoggedOut: Logout
    LoggedOut --> [*]
```

### Order Status Flow

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Confirmed: Payment OK
    Pending --> Cancelled: Payment Failed
    Confirmed --> Shipped: Ready
    Shipped --> Delivered: Received
    Cancelled --> [*]
    Delivered --> [*]
```

## 5. Entity-Relationship (ER) Diagram

### Simple Database Schema

```mermaid
erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ COMMENT : writes
    POST ||--o{ COMMENT : receives
    
    USER {
        int id PK
        string email
        string password_hash
        datetime created_at
    }
    
    POST {
        int id PK
        int user_id FK
        string title
        string content
        datetime created_at
    }
    
    COMMENT {
        int id PK
        int post_id FK
        int user_id FK
        string text
        datetime created_at
    }
```

### E-commerce Database

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    PRODUCT ||--o{ CATEGORY : belongs
    
    CUSTOMER {
        int id PK
        string name
        string email
        string address
    }
    
    CATEGORY {
        int id PK
        string name
    }
    
    PRODUCT {
        int id PK
        int category_id FK
        string name
        float price
        int stock
    }
    
    ORDER {
        int id PK
        int customer_id FK
        datetime date
        float total
    }
    
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
    }
```

## Common Patterns

### Input Validation Pattern

```mermaid
flowchart TD
    A[Input] --> B{Valid?}
    B -->|No| C[Error Message]
    C --> A
    B -->|Yes| D[Process]
    D --> E[Success]
```

### API Endpoint Pattern

```mermaid
flowchart TD
    A[Request] --> B{Method?}
    B -->|GET| C[Retrieve]
    B -->|POST| D[Create]
    B -->|PUT| E[Update]
    B -->|DELETE| F[Delete]
    C --> G[Response]
    D --> G
    E --> G
    F --> G
```

### Error Handling Pattern

```mermaid
flowchart TD
    A[Try] --> B{Success?}
    B -->|Yes| C[Return Result]
    B -->|No| D[Catch Exception]
    D --> E{Recoverable?}
    E -->|Yes| F[Retry]
    E -->|No| G[Log Error]
    F --> B
    G --> H[Return Error]
    C --> I[End]
    H --> I
```

### Database Query Pattern

```mermaid
flowchart TD
    A[Query] --> B[Connect]
    B --> C[Execute]
    C --> D{Results?}
    D -->|Found| E[Map to Model]
    D -->|None| F[Empty Result]
    E --> G[Return]
    F --> G
    G --> H[Close Connection]
```

## Tips

1. **Use IDs** for nodes, not long labels
2. **Keep it simple** — max 15-20 nodes
3. **Use consistent naming** — camelCase or snake_case
4. **Group related items** — same direction flow
5. **Label arrows** — explain transitions
6. **Color strategically** — highlight important paths

## Next Steps

- Learn [INTERMEDIATE_DIAGRAMS.md](INTERMEDIATE_DIAGRAMS.md) for state machines, git graphs
- See [BEST_PRACTICES.md](BEST_PRACTICES.md) for optimization
- Use [CLI_REFERENCE.md](CLI_REFERENCE.md) for rendering
