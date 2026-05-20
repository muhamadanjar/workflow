# Mermaid Best Practices

Optimization, styling, performance, integration.

## 1. Readability

### Good: Clear, Simple, Readable

```mermaid
flowchart TD
    A[User Input]
    B{Validate}
    C[Process]
    D[Output]
    
    A --> B
    B -->|Valid| C
    B -->|Invalid| A
    C --> D
```

### Bad: Cluttered, Hard to Follow

```mermaid
flowchart TD
    A["User Input"] --> B["Long Process Description That Takes Multiple Lines"] --> C["Another Complex Process With Details"] --> D["Final Output With Additional Information"]
    B -.->|Error| A
```

**Rules:**
- Max 15-20 nodes per diagram
- Use descriptive but short labels
- Clear directional flow
- Group related items

## 2. Styling & Colors

### Color by Category

```mermaid
flowchart TD
    A[User Input]:::userClass
    B{Validate}:::processClass
    C[Error]:::errorClass
    D[Success]:::successClass
    
    A --> B
    B -->|Fail| C
    B -->|Pass| D
    
    classDef userClass fill:#e1f5ff
    classDef processClass fill:#f3e5f5
    classDef errorClass fill:#ffebee
    classDef successClass fill:#e8f5e9
```

### Consistent Styling

```mermaid
flowchart TD
    A[Start]:::start
    B[Process 1]:::process
    C[Decision]:::decision
    D[Error]:::error
    E[End]:::end
    
    A --> B
    B --> C
    C -->|Fail| D
    C -->|Pass| E
    
    classDef start fill:#4CAF50,color:#fff
    classDef process fill:#2196F3,color:#fff
    classDef decision fill:#FF9800,color:#fff
    classDef error fill:#f44336,color:#fff
    classDef end fill:#9C27B0,color:#fff
```

## 3. Performance Optimization

### Break Large Diagrams

**Bad: One huge diagram (50+ nodes)**
```
Too complex, hard to understand, slow to render
```

**Good: Multiple focused diagrams**
```
1. System Context (5 nodes)
2. User Flow (8 nodes)
3. Data Flow (7 nodes)
4. Architecture (12 nodes)
```

### Use Direction Wisely

```mermaid
% LR = more compact
flowchart LR
    A[Start] --> B[Process] --> C[End]
```

```mermaid
% TD = better for long flows
flowchart TD
    A[Step 1]
    A --> B[Step 2]
    B --> C[Step 3]
    C --> D[Step 4]
    D --> E[Step 5]
```

## 4. Documentation Integration

### In GitHub README

```markdown
# System Architecture

```mermaid
graph TB
    Client[Client]
    API[API Server]
    DB[(Database)]
    
    Client --> API
    API --> DB
`​``

## 5. Version Control

### Store .mmd Files

```bash
# Good: Version control
diagrams/
├── user-flow.mmd
├── database-schema.mmd
├── api-architecture.mmd
└── deployment.mmd
```

### Generate Images in CI/CD

```yaml
# GitHub Actions
- name: Render Diagrams
  run: |
    mmdc -i diagrams/*.mmd -o diagrams/rendered/
    git add diagrams/rendered/
```

## 6. Naming Conventions

### Clear Node IDs

```mermaid
flowchart TD
    START[Start]
    VALIDATE{Validate Input}
    PROCESS[Process Data]
    ERROR[Error Handler]
    SUCCESS[Send Success]
    
    START --> VALIDATE
    VALIDATE -->|Valid| PROCESS
    VALIDATE -->|Invalid| ERROR
    PROCESS --> SUCCESS
```

### Consistent Labels

```
% Good:
- CreateUser
- DeletePost
- CheckInventory

% Bad:
- make user
- get rid of post
- does warehouse have it?
```

## 7. Sequence Diagram Tips

### Manage Complexity

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    
    U->>F: Click Login
    F->>B: POST /login
    rect rgb(200, 150, 255)
        Note over B: Authenticate
        B->>B: Hash Password
        B->>B: Compare
    end
    B-->>F: Token
    F-->>U: Redirect
```

### Use Loops for Repetition

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    loop Every 5 seconds
        Client->>Server: Health Check
        Server-->>Client: OK
    end
```

## 8. Class Diagram Best Practices

### Limit Inheritance Depth

```mermaid
classDiagram
    class Animal
    class Mammal
    class Dog
    
    Animal <|-- Mammal
    Mammal <|-- Dog
```

### Use Composition Over Deep Hierarchy

```mermaid
classDiagram
    class User
    class Profile
    class Address
    
    User "1" --> "1" Profile
    User "1" --> "0..*" Address
```

## 9. Testing Diagrams

### Syntax Validation

```bash
# Use online editor
https://mermaid.live

# Or CLI validation
mmdc -i diagram.mmd --configFile config.json
```

### Rendering Quality

```bash
# High quality SVG
mmdc -i diagram.mmd -o output.svg -t default

# PDF for printing
mmdc -i diagram.mmd -o output.pdf
```

## 10. Common Mistakes

### ❌ Too Much Information

```mermaid
flowchart TD
    A["User Enters Email and Password Details\nThen System Validates Format and\nConnects to Database Server"]
```

### ✅ Concise Labels

```mermaid
flowchart TD
    A[User Input]
    B{Validate}
```

### ❌ Unclear Flow

```mermaid
flowchart TD
    A --> B
    B --> C
    C --> D
    D --> A
    E --> B
    C --> E
```

### ✅ Clear Structure

```mermaid
flowchart TD
    A --> B --> C --> D
    E --> B
    C --> E
```

### ❌ Wrong Diagram Type

```
Using sequence diagram for process flow
Using flowchart for database relationships
Using class diagram for simple hierarchy
```

### ✅ Right Choice

```
Process flow → Flowchart
Communication → Sequence
Database → ER Diagram
State changes → State Diagram
```

## 11. Accessibility

### Add Descriptions

```mermaid
%%{init: {'logLevel': 'debug', 'theme': 'base'} }%%
flowchart TD
    A["Login Page\n(Enter Credentials)"]
    B["Authentication Service\n(Verify User)"]
    C{"Credentials\nValid?"}
    
    A --> B
    B --> C
```

### Use Alt Text

```markdown
![Authentication Flow](./auth-flow.mmd)
*Diagram: User login flow with credential validation*
```

## 12. Performance Monitoring

### Rendering Time

```bash
# Time rendering
time mmdc -i large-diagram.mmd -o output.png

# Profile with custom config
mmdc -i diagram.mmd -o output.png -c optimize.json
```

### Optimization Config

```json
{
  "flowchart": {
    "htmlLabels": true,
    "useMaxWidth": true
  },
  "sequence": {
    "messageAlign": "center"
  }
}
```

## Checklist

Before publishing:

- [ ] Diagram is clear (max 20 nodes)
- [ ] Labels are concise and meaningful
- [ ] Colors are consistent
- [ ] Direction is consistent (TD/LR)
- [ ] No loops or unclear flows
- [ ] Tested in renderer
- [ ] Renders to PNG/SVG correctly
- [ ] Fits page when printed
- [ ] Documentation complete
- [ ] In version control

## Resources

- [Mermaid Config](https://mermaid.js.org/config/configuration.html)
- [Styling Guide](https://mermaid.js.org/syntax/flowchart.html#styling-and-classes)
- [Theme Options](https://mermaid.js.org/syntax/flowchart.html#theme-variables)
