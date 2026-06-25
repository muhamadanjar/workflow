# GraphQL Performance Optimization

Query analysis, caching, and optimization strategies.

## Query Analysis

### N+1 Problem

**Bad:**
```typescript
const resolvers = {
  Query: {
    users: async () => User.find() // 1 query
  },
  User: {
    orders: async (user) => {
      // Called N times for N users = N+1 queries!
      return Order.find({ userId: user.id });
    }
  }
};
```

**Good (DataLoader):**
```typescript
const orderLoader = new DataLoader(async (userIds) => {
  // Single query for all userIds
  const orders = await Order.find({ userId: { $in: userIds } });
  return userIds.map(id => 
    orders.filter(o => o.userId === id)
  );
});

const resolvers = {
  User: {
    orders: (user, _, { orderLoader }) => {
      return orderLoader.load(user.id);
    }
  }
};
```

## Query Depth Limiting

Prevent expensive nested queries.

```typescript
import { validate, buildSchema } from 'graphql';

const depthLimitRule = (maxDepth = 3) => {
  return {
    Field(node) {
      let depth = 1;
      let parent = node.parent;
      while (parent) {
        if (parent.kind === 'Field') depth++;
        parent = parent.parent;
      }
      if (depth > maxDepth) {
        context.addError(
          new GraphQLError(
            `Query exceeds max depth of ${maxDepth}`,
            [node]
          )
        );
      }
    }
  };
};

// Use in server
app.post('/graphql', async (req, res) => {
  const errors = validate(schema, parse(req.body.query), [
    depthLimitRule(3)
  ]);
  if (errors.length > 0) {
    return res.status(400).json({ errors });
  }
  // ...
});
```

## Query Complexity Analysis

```typescript
import { getComplexity, simpleEstimator } from 'graphql-query-complexity';

app.post('/graphql', async (req, res) => {
  const complexity = getComplexity({
    schema,
    operationName: req.body.operationName,
    query: parse(req.body.query),
    variables: req.body.variables,
    estimators: [simpleEstimator({ defaultComplexity: 1 })]
  });

  if (complexity > 1000) {
    return res.status(400).json({
      error: 'Query too complex'
    });
  }
});
```

## Caching Strategies

### HTTP Caching

```typescript
const typeDefs = gql`
  directive @cacheControl(maxAge: Int) on FIELD_DEFINITION | OBJECT
  
  type User @cacheControl(maxAge: 3600) {
    id: ID!
    name: String!
  }
`;

app.use(responseCachePlugin());
```

### Field-Level Caching

```typescript
const fieldCache = new Map();

const resolvers = {
  Query: {
    user: async (_, { id }) => {
      const cacheKey = `user:${id}`;
      
      if (fieldCache.has(cacheKey)) {
        return fieldCache.get(cacheKey);
      }
      
      const user = await User.findById(id);
      fieldCache.set(cacheKey, user);
      
      setTimeout(() => fieldCache.delete(cacheKey), 3600000); // 1 hour
      
      return user;
    }
  }
};
```

### Redis Caching

```typescript
import redis from 'redis';

const cache = redis.createClient();

const resolvers = {
  Query: {
    users: async (_, { page = 1 }) => {
      const key = `users:page:${page}`;
      
      // Check cache
      const cached = await cache.get(key);
      if (cached) return JSON.parse(cached);
      
      // Fetch from DB
      const users = await User.find()
        .skip((page - 1) * 20)
        .limit(20);
      
      // Cache for 1 hour
      await cache.setex(key, 3600, JSON.stringify(users));
      
      return users;
    }
  }
};
```

## Pagination

Efficient data fetching without loading all records.

### Offset-Based

```graphql
type Query {
  users(page: Int! = 1, pageSize: Int! = 20): UserConnection!
}

type UserConnection {
  items: [User!]!
  total: Int!
  pages: Int!
}
```

### Cursor-Based (Better)

```graphql
type Query {
  users(first: Int!, after: String): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}
```

### Resolver

```typescript
const resolvers = {
  Query: {
    users: async (_, { first, after }) => {
      const query = {};
      
      if (after) {
        const decoded = Buffer.from(after, 'base64').toString();
        query._id = { $gt: decoded };
      }
      
      const users = await User.find(query)
        .limit(first + 1);
      
      const hasMore = users.length > first;
      const edges = users.slice(0, first).map(user => ({
        node: user,
        cursor: Buffer.from(user._id.toString()).toString('base64')
      }));
      
      return {
        edges,
        pageInfo: {
          hasNextPage: hasMore,
          endCursor: edges[edges.length - 1]?.cursor
        }
      };
    }
  }
};
```

## Fragment Caching

```typescript
const USER_FRAGMENT = gql`
  fragment UserFragment on User {
    id
    name
    email
  }
`;

// Client-side
export const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      ...UserFragment
    }
  }
  ${USER_FRAGMENT}
`;

// Server caches fragment parsing
```

## Batch Requests

Send multiple queries in one request.

```typescript
// Client
const results = await client.query({
  query: gql`
    query {
      user1: user(id: "1") { id name }
      user2: user(id: "2") { id name }
      user3: user(id: "3") { id name }
    }
  `
});
```

## Persisted Queries

Pre-send query hashes instead of full query strings.

```typescript
// Client-side
import { createPersistedQueryLink } from '@apollo/client/link/persisted-queries';
import { sha256 } from 'crypto-js';

const link = createPersistedQueryLink({
  sha256Fn: (document) => sha256(document).toString(),
  useGETForHashedQueries: true
});

// Server-side
const persistedQueries = new Map([
  ['hash1', 'query GetUser($id: ID!) { user(id: $id) { id name } }'],
  ['hash2', 'query GetUsers { users { id name } }']
]);

app.post('/graphql', (req, res) => {
  if (req.body.extensions?.persistedQuery?.sha256Hash) {
    const hash = req.body.extensions.persistedQuery.sha256Hash;
    const query = persistedQueries.get(hash);
    if (!query) {
      return res.status(400).json({ error: 'Unknown query hash' });
    }
    req.body.query = query;
  }
  // Process request
});
```

## Database Query Optimization

### Eager Loading

```typescript
const resolvers = {
  Query: {
    users: async () => {
      // Load users with orders in one query
      return User.find().populate('orders');
    }
  }
};
```

### Projection

```typescript
const resolvers = {
  Query: {
    users: async (_, __, ___, info) => {
      // Extract requested fields
      const fields = getFieldNames(info.fieldNodes[0]);
      
      // Only select needed fields
      const projection = {};
      fields.forEach(f => projection[f] = 1);
      
      return User.find({}, projection);
    }
  }
};

function getFieldNames(node) {
  return node.selectionSet.selections.map(s => s.name.value);
}
```

## Monitoring

### Query Metrics

```typescript
import { plugin } from 'apollo-server-plugin';

const metricsPlugin = {
  async willResolveField() {
    const start = Date.now();
    return () => {
      const duration = Date.now() - start;
      logger.info('Resolver time', {
        field: info.fieldName,
        duration
      });
    };
  }
};

new ApolloServer({
  schema,
  plugins: [metricsPlugin]
});
```

### Slow Query Detection

```typescript
app.post('/graphql', async (req, res) => {
  const start = Date.now();
  
  const result = await graphql(schema, req.body.query);
  
  const duration = Date.now() - start;
  if (duration > 1000) {
    logger.warn('Slow query', {
      query: req.body.query,
      duration
    });
  }
  
  res.json(result);
});
```

---

Last Updated: 2026-06-25
