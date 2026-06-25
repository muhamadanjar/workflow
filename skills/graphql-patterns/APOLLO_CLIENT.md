# Apollo Client — React Integration

GraphQL client for React with caching, state management, and hooks.

## Setup

```bash
npm install @apollo/client graphql
```

## Basic Configuration

```typescript
import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client';

const client = new ApolloClient({
  link: new HttpLink({ uri: 'http://localhost:4000/graphql' }),
  cache: new InMemoryCache(),
});
```

## Provider Setup

```tsx
import { ApolloProvider } from '@apollo/client';

<ApolloProvider client={client}>
  <App />
</ApolloProvider>
```

## Queries

### useQuery Hook

```typescript
import { gql, useQuery } from '@apollo/client';

const GET_USERS = gql`
  query GetUsers($page: Int!) {
    users(page: $page) {
      id
      name
      email
    }
  }
`;

export function UserList() {
  const { data, loading, error } = useQuery(GET_USERS, {
    variables: { page: 1 }
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {data.users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### Query Options

```typescript
useQuery(GET_USERS, {
  variables: { page: 1 },
  fetchPolicy: 'cache-first',      // Default: use cache if available
  pollInterval: 10000,              // Poll every 10s
  notifyOnNetworkStatusChange: true, // Refetch indicator
  skip: !userId,                    // Skip if condition false
  onCompleted: (data) => { },       // Success callback
  onError: (error) => { },          // Error callback
});
```

### Fetch Policies

```
'cache-first'    — Use cache, fetch if missing
'cache-and-network' — Use cache, fetch in background
'network-only'   — Always fetch from server
'no-cache'       — No cache, fetch every time
'cache-only'     — Only cache, never fetch
```

## Mutations

### useMutation Hook

```typescript
const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      id
      name
      email
    }
  }
`;

export function CreateUserForm() {
  const [createUser, { loading, error }] = useMutation(CREATE_USER, {
    onCompleted: (data) => {
      console.log('User created:', data.createUser);
    },
  });

  const handleSubmit = async (formData) => {
    await createUser({
      variables: { input: formData }
    });
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Cache Updates

```typescript
const [createUser] = useMutation(CREATE_USER, {
  update(cache, { data: { createUser } }) {
    // Manually update cache
    cache.modify({
      fields: {
        users(existingUsers = []) {
          return [...existingUsers, createUser];
        }
      }
    });
  }
});
```

## Subscriptions

```typescript
import { useSubscription } from '@apollo/client';

const USER_ADDED = gql`
  subscription OnUserAdded {
    userAdded {
      id
      name
    }
  }
`;

export function UserNotifications() {
  const { data, loading } = useSubscription(USER_ADDED);

  return (
    <div>
      {data?.userAdded && <p>New user: {data.userAdded.name}</p>}
    </div>
  );
}
```

## Caching

### InMemoryCache

```typescript
const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        users: {
          merge(existing, incoming) {
            return incoming;
          }
        }
      }
    }
  }
});
```

### Reading from Cache

```typescript
const user = client.cache.readQuery({
  query: GET_USER,
  variables: { id: '123' }
});
```

### Writing to Cache

```typescript
client.cache.writeQuery({
  query: GET_USER,
  variables: { id: '123' },
  data: { user: { id: '123', name: 'John' } }
});
```

## Error Handling

```typescript
import { ApolloError } from '@apollo/client';

const { data, error } = useQuery(GET_USERS);

if (error instanceof ApolloError) {
  if (error.networkError) {
    console.log('Network error:', error.networkError);
  }
  if (error.graphQLErrors) {
    error.graphQLErrors.forEach(err => {
      console.log('GraphQL error:', err.message);
    });
  }
}
```

## Custom Hooks

```typescript
export function useGetUser(id: string) {
  return useQuery(GET_USER, {
    variables: { id },
    skip: !id,
  });
}

export function useCreateUser() {
  return useMutation(CREATE_USER, {
    refetchQueries: [{ query: GET_USERS }],
  });
}
```

## Authentication

```typescript
import { setContext } from '@apollo/client/link/context';

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('token');
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    }
  };
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});
```

## Performance Tips

1. **Use fragments** — Reuse query parts
2. **Pagination** — Don't fetch all records
3. **Cache policy** — Choose right strategy
4. **Lazy queries** — useLazyQuery for on-demand
5. **Batch requests** — Use batching links
6. **Persisted queries** — Reduce payload size

---

Last Updated: 2026-06-25
