# Advanced GraphQL — Federation, Subscriptions, Fragments

Enterprise patterns for complex GraphQL systems.

## Schema Federation

Compose multiple GraphQL services into unified schema.

### Base Service

```graphql
# Users service
type Query {
  user(id: ID!): User
  users: [User!]!
}

type User @key(fields: "id") {
  id: ID!
  name: String!
  email: String!
}
```

### Extending Service

```graphql
# Orders service
extend type User @key(fields: "id") {
  id: ID! @external
  orders: [Order!]!
}

type Order {
  id: ID!
  userId: ID!
  total: Float!
}

type Query {
  order(id: ID!): Order
}
```

### Apollo Federation Setup

```typescript
import { buildSubgraphSchema } from '@apollo/subgraph';

const schema = buildSubgraphSchema([
  {
    typeDefs: gql`
      type User @key(fields: "id") {
        id: ID!
        name: String!
      }
    `,
    resolvers: {
      User: {
        __resolveReference(user) {
          return findUserById(user.id);
        }
      }
    }
  }
]);
```

### Apollo Gateway

```typescript
import { ApolloGateway, IntrospectAndCompose } from '@apollo/gateway';
import { ApolloServer } from 'apollo-server-express';

const gateway = new ApolloGateway({
  supergraphSdl: new IntrospectAndCompose({
    subgraphs: [
      { name: 'users', url: 'http://users-service:4001/graphql' },
      { name: 'orders', url: 'http://orders-service:4002/graphql' }
    ]
  })
});

const server = new ApolloServer({ gateway });
```

## Real-Time Subscriptions

### Server Setup

```typescript
import { WebSocketLink } from 'apollo-link-ws';
import { getMainDefinition } from '@apollo/client/utilities';

const wsLink = new WebSocketLink({
  uri: `ws://localhost:4000/graphql`,
  options: {
    reconnect: true,
    connectionParams: {
      authToken: localStorage.getItem('token'),
    }
  }
});

const httpLink = new HttpLink({ uri: 'http://localhost:4000/graphql' });

const link = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return definition.kind === 'OperationDefinition' &&
           definition.operation === 'subscription';
  },
  wsLink,
  httpLink,
);
```

### Subscription Definition

```graphql
type Subscription {
  userAdded: User!
  orderStatusChanged(userId: ID!): Order!
}
```

### Server Subscription

```typescript
const resolvers = {
  Subscription: {
    userAdded: {
      subscribe: () => pubsub.asyncIterator(['USER_ADDED'])
    },
    orderStatusChanged: {
      subscribe: (_, { userId }) =>
        pubsub.asyncIterator([`ORDER_STATUS_${userId}`])
    }
  },
  Mutation: {
    createUser: (_, { input }) => {
      const user = saveUser(input);
      pubsub.publish('USER_ADDED', { userAdded: user });
      return user;
    }
  }
};
```

### Client Subscription

```typescript
const USER_ADDED = gql`
  subscription OnUserAdded {
    userAdded {
      id
      name
    }
  }
`;

function UserNotifications() {
  const { data } = useSubscription(USER_ADDED);
  
  return data?.userAdded && <p>New: {data.userAdded.name}</p>;
}
```

## Fragments

Reusable query/mutation parts.

### Fragment Definition

```graphql
fragment UserFields on User {
  id
  name
  email
  createdAt
}

fragment OrderFields on Order {
  id
  total
  status
  createdAt
}
```

### Using Fragments

```graphql
query GetUserOrders($id: ID!) {
  user(id: $id) {
    ...UserFields
    orders {
      ...OrderFields
    }
  }
}
```

### Apollo Client Fragments

```typescript
import { gql } from '@apollo/client';

const USER_FRAGMENT = gql`
  fragment UserFragment on User {
    id
    name
    email
  }
`;

const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      ...UserFragment
    }
  }
  ${USER_FRAGMENT}
`;
```

## Directives

Schema directives for complex behavior.

### Built-in Directives

```graphql
query GetUser($includeEmail: Boolean!) {
  user(id: "1") {
    id
    name
    email @include(if: $includeEmail)
    age @skip(if: true)
  }
}
```

### Custom Directives

```typescript
const typeDefs = gql`
  directive @auth(role: String!) on FIELD_DEFINITION
  directive @rateLimit(limit: Int!) on FIELD_DEFINITION
  
  type Query {
    adminPanel: String @auth(role: "ADMIN")
    expensiveQuery: String @rateLimit(limit: 10)
  }
`;

const directiveResolvers = {
  auth: (next, source, args, context) => {
    if (context.user?.role !== args.role) {
      throw new Error('Unauthorized');
    }
    return next();
  },
  rateLimit: (next, source, args, context) => {
    if (context.rateLimiter.isExceeded(args.limit)) {
      throw new Error('Rate limited');
    }
    return next();
  }
};
```

## Batch Operations

Process multiple requests efficiently.

### DataLoader

```typescript
import DataLoader from 'dataloader';

const userLoader = new DataLoader(async (userIds) => {
  const users = await User.find({ id: { $in: userIds } });
  return userIds.map(id => users.find(u => u.id === id));
});

const resolvers = {
  Order: {
    user: (order, _, context) => {
      return context.userLoader.load(order.userId);
    }
  }
};

// Setup in context
app.post('/graphql', (req, res) => {
  const context = {
    userLoader: new DataLoader(...)
  };
  // ...
});
```

## Interface Implementation

Share fields across types.

```graphql
interface Node {
  id: ID!
  createdAt: DateTime!
}

type User implements Node {
  id: ID!
  createdAt: DateTime!
  name: String!
}

type Order implements Node {
  id: ID!
  createdAt: DateTime!
  total: Float!
}

type Query {
  node(id: ID!): Node
}
```

### Resolver

```typescript
const resolvers = {
  Node: {
    __resolveType(obj) {
      if (obj.name) return 'User';
      if (obj.total) return 'Order';
      return null;
    }
  },
  Query: {
    node: (_, { id }) => {
      // Return any node type
      return findNodeById(id);
    }
  }
};
```

## Union Types

Flexible return types.

```graphql
union SearchResult = User | Order | Product

type Query {
  search(query: String!): [SearchResult!]!
}
```

### Resolver

```typescript
const resolvers = {
  SearchResult: {
    __resolveType(obj) {
      if (obj.email) return 'User';
      if (obj.total) return 'Order';
      if (obj.price) return 'Product';
      return null;
    }
  },
  Query: {
    search: async (_, { query }) => {
      const results = await Promise.all([
        User.find({ name: { $regex: query } }),
        Order.find({ id: { $regex: query } }),
        Product.find({ name: { $regex: query } })
      ]);
      return results.flat();
    }
  }
};
```

## Input Types

Structured mutation arguments.

```graphql
input CreateUserInput {
  name: String!
  email: String!
  password: String!
}

input UpdateUserInput {
  id: ID!
  name: String
  email: String
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(input: UpdateUserInput!): User!
}
```

---

Last Updated: 2026-06-25
