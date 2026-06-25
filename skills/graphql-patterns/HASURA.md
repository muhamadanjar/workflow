# Hasura — Instant GraphQL APIs

Automatically generate GraphQL APIs from databases with permissions and business logic.

## Setup

### Docker Compose

```yaml
version: '3.6'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"

  hasura:
    image: hasura/graphql-engine:latest
    environment:
      HASURA_GRAPHQL_DATABASE_URL: postgres://postgres:postgres@postgres:5432/postgres
      HASURA_GRAPHQL_ENABLE_CONSOLE: "true"
      HASURA_GRAPHQL_DEV_MODE: "true"
      HASURA_GRAPHQL_ADMIN_SECRET: secret
    ports:
      - "8080:8080"
    depends_on:
      - postgres
```

### Start

```bash
docker-compose up
# Visit http://localhost:8080/console
```

## Database Tables

Create tables, Hasura auto-generates GraphQL.

### Example Schema

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID NOT NULL REFERENCES posts(id),
  user_id UUID NOT NULL REFERENCES users(id),
  text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Auto-Generated API

```graphql
# Hasura auto-generates all these queries

type Query {
  users: [User!]!
  users_by_pk(id: UUID!): User
  posts: [Post!]!
  posts_by_pk(id: UUID!): Post
  comments: [Comment!]!
  comments_by_pk(id: UUID!): Comment
}

type Mutation {
  insert_users(objects: [UserInput!]!): InsertUserResponse!
  update_users(...): UpdateUserResponse!
  delete_users(...): DeleteUserResponse!
  # ... and mutations for posts, comments
}

type User {
  id: UUID!
  name: String!
  email: String!
  posts: [Post!]!
  comments: [Comment!]!
  created_at: DateTime!
}

type Post {
  id: UUID!
  user_id: UUID!
  user: User!
  title: String!
  content: String
  comments: [Comment!]!
  created_at: DateTime!
}

type Comment {
  id: UUID!
  post_id: UUID!
  post: Post!
  user_id: UUID!
  user: User!
  text: String!
  created_at: DateTime!
}
```

## Permissions & Row-Level Security

### Define Permissions

**Console:** Tables → Permissions tab

Set per-table access control.

### Example: Users Table

```
Select permission (authenticated role):
  With custom check: { "user_id": { "_eq": "X-Hasura-User-Id" } }
  Columns: id, name, email (hide password)

Insert permission (authenticated role):
  With custom check: { "user_id": { "_eq": "X-Hasura-User-Id" } }
  Column preset: user_id = X-Hasura-User-Id

Update permission (authenticated role):
  With custom check: { "user_id": { "_eq": "X-Hasura-User-Id" } }
  Only these columns: name, email

Delete permission (authenticated role):
  With custom check: { "user_id": { "_eq": "X-Hasura-User-Id" } }
```

### Anonymous Access (Public)

```
Select (anonymous):
  Without any checks
  Columns: id, name, created_at
  
Update/Delete: disabled
Insert: disabled
```

## Custom Resolvers

Add custom logic with webhooks.

### Example: Create User with Auth

```yaml
# On Users table, add action
Name: create_user
Type: Mutation
Inputs:
  - email: String!
  - password: String!
  - name: String!
Outputs:
  - id: UUID!
  - email: String!
  - name: String!
  - access_token: String!

Webhook: http://localhost:3000/auth/signup
```

### Handler

```typescript
// http://localhost:3000/auth/signup
app.post('/auth/signup', async (req, res) => {
  const { email, password, name } = req.body.input;

  // Validate
  if (!email || !password || !name) {
    return res.status(400).json({ error: 'Missing fields' });
  }

  // Hash password
  const hashedPassword = await bcrypt.hash(password, 10);

  // Create user in Hasura
  const result = await fetch('http://localhost:8080/v1/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Hasura-Admin-Secret': process.env.HASURA_ADMIN_SECRET
    },
    body: JSON.stringify({
      query: `mutation {
        insert_users_one(object: {
          email: "${email}",
          name: "${name}",
          password_hash: "${hashedPassword}"
        }) {
          id
          email
          name
        }
      }`
    })
  }).then(r => r.json());

  // Generate JWT
  const token = jwt.sign(
    { user_id: result.data.insert_users_one.id },
    process.env.JWT_SECRET
  );

  res.json({
    ...result.data.insert_users_one,
    access_token: token
  });
});
```

## Remote Schemas

Extend Hasura with external GraphQL APIs.

### Configure

Console → Remote Schemas → Add

```
Name: external-api
GraphQL Server URL: https://api.example.com/graphql
```

### Extend Type

```graphql
# External API has type Product
type Product {
  id: ID!
  name: String!
}

# Local User table
type User {
  id: UUID!
  name: String!
}

# Extend User to access external Products
extend type User {
  products: [Product!]!
}
```

### Resolver

Map User to Product via webhook or direct link.

## Event Triggers

Trigger functions on data changes.

### Setup

Console → Events → Create trigger

```
Table: users
Events: insert, update, delete
Webhook: http://localhost:3000/webhooks/user-changed
```

### Handler

```typescript
app.post('/webhooks/user-changed', async (req, res) => {
  const { event } = req.body;
  
  if (event.op === 'INSERT') {
    const user = event.data.new;
    // Send welcome email
    await sendEmail(user.email, 'Welcome!');
  }
  
  if (event.op === 'UPDATE') {
    const oldUser = event.data.old;
    const newUser = event.data.new;
    // Handle profile update
  }
  
  if (event.op === 'DELETE') {
    const user = event.data.old;
    // Cleanup
  }
  
  res.json({ success: true });
});
```

## Relationships

Define relationships for joins.

### One-to-Many

```
Users (1) → (Many) Posts
Foreign key: posts.user_id → users.id
```

Query automatically resolves:

```graphql
{
  users {
    id
    name
    posts {
      id
      title
    }
  }
}
```

### Many-to-Many

```
Users ←→ Posts (through post_likes)

post_likes table:
- user_id (FK users)
- post_id (FK posts)
```

Define two relationships:
- Users has many post_likes
- post_likes has one Post

Query:

```graphql
{
  users {
    post_likes {
      post {
        title
      }
    }
  }
}
```

## Subscriptions

Real-time data streaming.

### Enable WebSocket

```yaml
environment:
  HASURA_GRAPHQL_WEBSOCKET_CONNECTION_INIT_TIMEOUT: "60"
```

### Subscribe

```typescript
const subscription = gql`
  subscription OnPostAdded {
    posts(order_by: { created_at: desc }, limit: 10) {
      id
      title
      user { name }
    }
  }
`;

const { data } = useSubscription(subscription);
```

## Performance Tips

1. **Indexes** — Add on frequently filtered columns
   ```sql
   CREATE INDEX idx_posts_user_id ON posts(user_id);
   CREATE INDEX idx_comments_post_id ON comments(post_id);
   ```

2. **Query Caching** — Hasura caches prepared statements

3. **Permission Optimization** — Simple checks (vs complex logic)

4. **Connections** — Set max pool size
   ```yaml
   environment:
     HASURA_GRAPHQL_DB_POOL_SIZE: "50"
   ```

## Production Deployment

### Environment

```yaml
HASURA_GRAPHQL_DATABASE_URL: ${DATABASE_URL}
HASURA_GRAPHQL_ADMIN_SECRET: ${ADMIN_SECRET}
HASURA_GRAPHQL_JWT_SECRET: '{"type":"HS256","key":"secret"}'
HASURA_GRAPHQL_ENABLED_LOG_TYPES: "startup,http-log,webhook-log"
HASURA_GRAPHQL_ENABLE_CONSOLE: "false"
```

### Monitoring

Enable logs:

```
startup, http-log, query-log, webhook-log, websocket-log
```

Monitor:
- Query execution time
- Database connections
- Event trigger failures
- WebSocket connections

## Migration

Export schema as code (migrations):

```bash
hasura migrate create init --from-server
hasura migrate apply --database-name default
```

---

Last Updated: 2026-06-25
