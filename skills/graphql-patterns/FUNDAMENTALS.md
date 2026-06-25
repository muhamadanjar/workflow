# GraphQL Fundamentals

## Schema Definition

```graphql
type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
  search(query: String!): [SearchResult!]!
}

type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
}

type Comment {
  id: ID!
  text: String!
  author: User!
  post: Post!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
  createPost(input: CreatePostInput!): Post!
}

type Subscription {
  userCreated: User!
  postPublished: Post!
  commentAdded(postId: ID!): Comment!
}

# Input types
input CreateUserInput {
  name: String!
  email: String!
}

input UpdateUserInput {
  name: String
  email: String
}

# Scalars
scalar DateTime
```

## Query Examples

```graphql
# Simple query
{
  user(id: "1") {
    id
    name
    email
  }
}

# With relationships
{
  user(id: "1") {
    name
    posts {
      title
      comments {
        text
        author {
          name
        }
      }
    }
  }
}

# With variables
query GetUser($userId: ID!) {
  user(id: $userId) {
    name
    email
    posts {
      title
    }
  }
}

# Fragment
fragment UserFields on User {
  id
  name
  email
  createdAt
}

query {
  user(id: "1") {
    ...UserFields
  }
}

# Multiple queries
{
  user1: user(id: "1") {
    name
  }
  user2: user(id: "2") {
    name
  }
}
```

## Resolvers

```javascript
// Apollo Server resolvers
const resolvers = {
  Query: {
    user: (_, { id }) => {
      return db.users.findById(id);
    },
    users: (_, { limit = 10, offset = 0 }) => {
      return db.users.find().limit(limit).skip(offset);
    }
  },
  
  User: {
    posts: (user) => {
      return db.posts.find({ authorId: user.id });
    }
  },
  
  Post: {
    author: (post) => {
      return db.users.findById(post.authorId);
    },
    comments: (post) => {
      return db.comments.find({ postId: post.id });
    }
  },
  
  Mutation: {
    createUser: (_, { input }) => {
      const user = { ...input, id: generateId() };
      db.users.insert(user);
      return user;
    },
    updateUser: (_, { id, input }) => {
      const user = db.users.findByIdAndUpdate(id, input);
      return user;
    }
  },
  
  Subscription: {
    userCreated: {
      subscribe: (_, __, { pubsub }) => {
        return pubsub.asyncIterator(['USER_CREATED']);
      }
    }
  }
};
```

## Directives

```graphql
# Skip/Include directives
{
  user(id: "1") {
    name
    email @include(if: $includeEmail)
    posts @skip(if: $skipPosts) {
      title
    }
  }
}

# Custom directives
directive @auth(requires: Role!) on FIELD_DEFINITION

type Query {
  adminUsers: [User!]! @auth(requires: ADMIN)
}
```

## Errors

```javascript
// Throw errors in resolvers
const resolvers = {
  Query: {
    user: (_, { id }) => {
      if (!id) {
        throw new GraphQLError('User ID required', {
          extensions: {
            code: 'BAD_REQUEST'
          }
        });
      }
      
      const user = db.users.findById(id);
      if (!user) {
        throw new GraphQLError('User not found', {
          extensions: {
            code: 'NOT_FOUND'
          }
        });
      }
      
      return user;
    }
  }
};
```

## Input Validation

```javascript
import { GraphQLError } from 'graphql';

const resolvers = {
  Mutation: {
    createUser: (_, { input }) => {
      // Validate
      if (!input.email.includes('@')) {
        throw new GraphQLError('Invalid email', {
          extensions: { code: 'INVALID_EMAIL' }
        });
      }
      
      if (input.name.length < 3) {
        throw new GraphQLError('Name too short', {
          extensions: { code: 'VALIDATION_ERROR' }
        });
      }
      
      // Create
      const user = { ...input, id: generateId() };
      db.users.insert(user);
      return user;
    }
  }
};
```

## Best Practices

- ✅ Design schema for use cases, not database
- ✅ Use non-null (!) for required fields
- ✅ Namespace mutations by entity
- ✅ Use input types for mutations
- ✅ Implement pagination for lists
- ✅ Validate input
- ✅ Handle errors properly
- ✅ Use fragments for reuse
