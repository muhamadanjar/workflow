# Apollo Server

## Setup

```javascript
import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';

const typeDefs = `
  type Query {
    hello: String
    user(id: ID!): User
  }
  
  type User {
    id: ID!
    name: String!
  }
`;

const resolvers = {
  Query: {
    hello: () => 'Hello world!',
    user: (_, { id }) => ({ id, name: 'John' })
  }
};

const server = new ApolloServer({
  typeDefs,
  resolvers
});

const { url } = await startStandaloneServer(server, {
  listen: { port: 4000 }
});

console.log(`Server running at ${url}`);
```

## With Express

```javascript
import express from 'express';
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';

const app = express();
app.use(express.json());

const server = new ApolloServer({
  typeDefs,
  resolvers
});

await server.start();

app.use('/graphql', expressMiddleware(server, {
  context: async ({ req }) => ({
    userId: req.headers['x-user-id']
  })
}));

app.listen(4000);
```

## Authentication

```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: async ({ req }) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      throw new GraphQLError('Not authenticated', {
        extensions: { code: 'UNAUTHENTICATED' }
      });
    }
    
    const user = verifyToken(token);
    return { user };
  }
});
```

## Middleware/Hooks

```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: {
    didResolveOperation: async (requestContext) => {
      console.log('Query:', requestContext.operationName);
    },
    willSendResponse: async (requestContext) => {
      console.log('Sending response');
    }
  }
});
```

## Data Loading (N+1 Prevention)

```javascript
import DataLoader from 'dataloader';

const createLoaders = () => ({
  userLoader: new DataLoader(async (userIds) => {
    return userIds.map(id => db.users.findById(id));
  }),
  postLoader: new DataLoader(async (postIds) => {
    return postIds.map(id => db.posts.findById(id));
  })
});

const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: () => ({
    loaders: createLoaders()
  })
});

// Use in resolvers
const resolvers = {
  Post: {
    author: (post, _, { loaders }) => {
      return loaders.userLoader.load(post.authorId);
    }
  }
};
```

## Subscriptions

```javascript
import { PubSub } from 'graphql-subscriptions';

const pubsub = new PubSub();

const typeDefs = `
  type Subscription {
    postPublished: Post!
  }
`;

const resolvers = {
  Subscription: {
    postPublished: {
      subscribe: () => pubsub.asyncIterator(['POST_PUBLISHED'])
    }
  },
  Mutation: {
    createPost: (_, { input }) => {
      const post = { ...input, id: generateId() };
      pubsub.publish('POST_PUBLISHED', { postPublished: post });
      return post;
    }
  }
};
```

## Error Handling

```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  formatError: (error) => {
    console.error(error);
    
    // Hide internal errors
    if (error.extensions?.code === 'INTERNAL_SERVER_ERROR') {
      return new GraphQLError('Something went wrong');
    }
    
    return error;
  }
});
```

## Best Practices

- ✅ Use DataLoader for batch loading
- ✅ Implement proper error handling
- ✅ Use context for shared data
- ✅ Validate input in resolvers
- ✅ Monitor query performance
- ✅ Use persisted queries
