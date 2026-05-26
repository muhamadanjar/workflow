# TanStack React Query v5 — Basic to Professional

## Installation

```bash
npm install @tanstack/react-query @tanstack/react-query-devtools
```

---

## Setup

```tsx
// app/providers.tsx (Next.js App Router)
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,     // 1 minute
            gcTime: 5 * 60 * 1000,    // 5 minutes (was cacheTime in v4)
            retry: 2,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

// app/layout.tsx
import { Providers } from "./providers";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

---

## Level 1: Basic useQuery

```tsx
// hooks/queries/useUsers.ts
import { useQuery } from "@tanstack/react-query";

interface User {
  id: string;
  name: string;
  email: string;
}

async function fetchUsers(): Promise<User[]> {
  const res = await fetch("/api/users");
  if (!res.ok) throw new Error("Failed to fetch users");
  return res.json();
}

export function useUsers() {
  return useQuery({
    queryKey: ["users"],
    queryFn: fetchUsers,
  });
}

// Usage in component
function UsersList() {
  const { data, isLoading, isError, error } = useUsers();

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {data?.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

---

## Level 2: Dynamic Query (by ID)

```tsx
// hooks/queries/useUser.ts
import { useQuery } from "@tanstack/react-query";

async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error("User not found");
  return res.json();
}

export function useUser(id: string | undefined) {
  return useQuery({
    queryKey: ["users", id],      // key includes id — refetches when id changes
    queryFn: () => fetchUser(id!),
    enabled: !!id,                // skip query if id is undefined
    staleTime: 5 * 60 * 1000,    // user data stays fresh 5 min
  });
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { data: user, isPending } = useUser(userId);

  if (isPending) return <Skeleton />;
  return <div>{user?.name}</div>;
}
```

---

## Level 3: useMutation (Create / Update / Delete)

```tsx
// hooks/mutations/useCreateUser.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";

interface CreateUserPayload {
  name: string;
  email: string;
}

async function createUser(payload: CreateUserPayload): Promise<User> {
  const res = await fetch("/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create user");
  return res.json();
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createUser,
    onSuccess: (newUser) => {
      // Invalidate users list — triggers refetch
      queryClient.invalidateQueries({ queryKey: ["users"] });

      // Or: add to cache directly (optimistic-like, no refetch)
      queryClient.setQueryData<User[]>(["users"], (old = []) => [...old, newUser]);
    },
    onError: (error) => {
      console.error("Create user failed:", error);
    },
  });
}

// Usage
function CreateUserForm() {
  const { mutate, isPending, isError, error } = useCreateUser();

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    mutate({
      name: form.get("name") as string,
      email: form.get("email") as string,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" placeholder="Name" required />
      <input name="email" type="email" placeholder="Email" required />
      {isError && <p className="text-red-500">{error.message}</p>}
      <button type="submit" disabled={isPending}>
        {isPending ? "Creating..." : "Create User"}
      </button>
    </form>
  );
}
```

---

## Level 4: Optimistic Updates

```tsx
// hooks/mutations/useUpdateUser.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<User> }) =>
      fetch(`/api/users/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }).then((r) => r.json()),

    onMutate: async ({ id, data }) => {
      // Cancel in-flight queries to avoid race
      await queryClient.cancelQueries({ queryKey: ["users", id] });

      // Snapshot current value
      const previous = queryClient.getQueryData<User>(["users", id]);

      // Optimistically update
      queryClient.setQueryData<User>(["users", id], (old) =>
        old ? { ...old, ...data } : old
      );

      // Return context for rollback
      return { previous };
    },

    onError: (_err, { id }, context) => {
      // Rollback on failure
      if (context?.previous) {
        queryClient.setQueryData(["users", id], context.previous);
      }
    },

    onSettled: (_data, _err, { id }) => {
      // Always refetch to sync with server
      queryClient.invalidateQueries({ queryKey: ["users", id] });
    },
  });
}
```

---

## Level 5: Infinite Query (Infinite Scroll)

```tsx
// hooks/queries/useInfiniteUsers.ts
import { useInfiniteQuery } from "@tanstack/react-query";

interface PageResult {
  data: User[];
  nextCursor: string | null;
}

async function fetchUsersPage({
  pageParam,
}: {
  pageParam: string | null;
}): Promise<PageResult> {
  const url = pageParam
    ? `/api/users?cursor=${pageParam}`
    : "/api/users";
  const res = await fetch(url);
  return res.json();
}

export function useInfiniteUsers() {
  return useInfiniteQuery({
    queryKey: ["users", "infinite"],
    queryFn: fetchUsersPage,
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });
}

// Usage with IntersectionObserver
import { useRef, useEffect } from "react";

function InfiniteUsersList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteUsers();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    if (bottomRef.current) observer.observe(bottomRef.current);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  const allUsers = data?.pages.flatMap((page) => page.data) ?? [];

  return (
    <div>
      {allUsers.map((user) => (
        <UserCard key={user.id} user={user} />
      ))}
      <div ref={bottomRef} className="h-4" />
      {isFetchingNextPage && <Spinner />}
    </div>
  );
}
```

---

## Level 6: Query Factory Pattern

### Centralized, type-safe query definitions

```tsx
// queries/userQueries.ts
import { queryOptions } from "@tanstack/react-query";

const userApi = {
  list: () => fetch("/api/users").then((r) => r.json() as Promise<User[]>),
  byId: (id: string) => fetch(`/api/users/${id}`).then((r) => r.json() as Promise<User>),
  stats: () => fetch("/api/users/stats").then((r) => r.json()),
};

export const userQueries = {
  all: () => ({ queryKey: ["users"] as const }),

  lists: () => ({
    ...userQueries.all(),
    queryKey: [...userQueries.all().queryKey, "list"] as const,
  }),

  list: (filters?: UserFilters) =>
    queryOptions({
      queryKey: [...userQueries.lists().queryKey, { filters }] as const,
      queryFn: () => userApi.list(),
    }),

  details: () => ({
    ...userQueries.all(),
    queryKey: [...userQueries.all().queryKey, "detail"] as const,
  }),

  detail: (id: string) =>
    queryOptions({
      queryKey: [...userQueries.details().queryKey, id] as const,
      queryFn: () => userApi.byId(id),
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
    }),

  stats: () =>
    queryOptions({
      queryKey: [...userQueries.all().queryKey, "stats"] as const,
      queryFn: userApi.stats,
    }),
};

// Usage — consistent keys everywhere
function useUsers(filters?: UserFilters) {
  return useQuery(userQueries.list(filters));
}

function useUser(id: string) {
  return useQuery(userQueries.detail(id));
}

// Invalidate all user queries
queryClient.invalidateQueries({ queryKey: userQueries.all().queryKey });

// Invalidate only detail queries
queryClient.invalidateQueries({ queryKey: userQueries.details().queryKey });
```

---

## Level 7: Prefetching + SSR (Next.js App Router)

### Server-side prefetch for instant load

```tsx
// app/users/page.tsx (Server Component)
import { dehydrate, HydrationBoundary, QueryClient } from "@tanstack/react-query";
import { userQueries } from "@/queries/userQueries";
import { UsersList } from "./UsersList";

export default async function UsersPage() {
  const queryClient = new QueryClient();

  // Prefetch on server
  await queryClient.prefetchQuery(userQueries.list());

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <UsersList />
    </HydrationBoundary>
  );
}

// app/users/UsersList.tsx (Client Component)
"use client";

import { useQuery } from "@tanstack/react-query";
import { userQueries } from "@/queries/userQueries";

export function UsersList() {
  // Data already in cache from server — no loading state
  const { data } = useQuery(userQueries.list());

  return (
    <ul>
      {data?.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### Prefetch on hover/focus

```tsx
function UserLink({ userId }: { userId: string }) {
  const queryClient = useQueryClient();

  const prefetch = () => {
    queryClient.prefetchQuery(userQueries.detail(userId));
  };

  return (
    <Link
      href={`/users/${userId}`}
      onMouseEnter={prefetch}
      onFocus={prefetch}
    >
      View Profile
    </Link>
  );
}
```

---

## Level 8: Advanced Patterns

### Dependent queries (sequential fetch)

```tsx
function useUserOrders(userId?: string) {
  const userQuery = useUser(userId ?? "");

  return useQuery({
    queryKey: ["orders", userQuery.data?.id],
    queryFn: () => fetchOrders(userQuery.data!.id),
    enabled: !!userQuery.data?.id,  // wait for user to load
  });
}
```

### Parallel queries

```tsx
function useDashboard() {
  const [usersQuery, ordersQuery, statsQuery] = useQueries({
    queries: [
      userQueries.list(),
      orderQueries.list(),
      userQueries.stats(),
    ],
  });

  return {
    users: usersQuery.data,
    orders: ordersQuery.data,
    stats: statsQuery.data,
    isLoading: usersQuery.isPending || ordersQuery.isPending || statsQuery.isPending,
    isError: usersQuery.isError || ordersQuery.isError || statsQuery.isError,
  };
}
```

### Global error handling

```tsx
import { QueryCache, MutationCache } from "@tanstack/react-query";

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      if (error instanceof UnauthorizedError) {
        router.push("/login");
        return;
      }
      toast.error(`Query failed: ${error.message}`);
    },
  }),
  mutationCache: new MutationCache({
    onError: (error) => {
      toast.error(error.message);
    },
  }),
});
```

### Polling / real-time

```tsx
function useLiveStatus(jobId: string) {
  return useQuery({
    queryKey: ["jobs", jobId, "status"],
    queryFn: () => fetchJobStatus(jobId),
    refetchInterval: (query) => {
      // Stop polling when done
      if (query.state.data?.status === "completed") return false;
      return 2000; // poll every 2s
    },
  });
}
```

### Suspense mode

```tsx
// Enable in queryOptions
const userQuery = queryOptions({
  queryKey: ["users", id],
  queryFn: () => fetchUser(id),
});

// Component
function UserProfile({ id }: { id: string }) {
  const { data } = useSuspenseQuery(userQueries.detail(id));
  // data is guaranteed non-undefined here
  return <div>{data.name}</div>;
}

// Parent wraps with Suspense
function Page() {
  return (
    <Suspense fallback={<Skeleton />}>
      <ErrorBoundary fallback={<ErrorState />}>
        <UserProfile id="123" />
      </ErrorBoundary>
    </Suspense>
  );
}
```

---

## API Client Pattern

### Axios-based typed client

```tsx
// lib/apiClient.ts
import axios from "axios";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor — attach token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — handle 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      queryClient.clear();
      router.push("/login");
    }
    return Promise.reject(error);
  }
);

// Typed request helpers
export const api = {
  get: <T>(url: string) => apiClient.get<T>(url).then((r) => r.data),
  post: <T>(url: string, data: unknown) => apiClient.post<T>(url, data).then((r) => r.data),
  patch: <T>(url: string, data: unknown) => apiClient.patch<T>(url, data).then((r) => r.data),
  delete: <T>(url: string) => apiClient.delete<T>(url).then((r) => r.data),
};
```

---

## React Query + Zustand (Hybrid State)

```tsx
// Server state → React Query
// Client/UI state → Zustand

// queries/userQueries.ts — server data
export const userQueries = {
  list: () => queryOptions({ queryKey: ["users"], queryFn: fetchUsers }),
};

// stores/uiStore.ts — UI state only
export const useUiStore = create<UiStore>((set) => ({
  selectedUserId: null,
  setSelectedUserId: (id) => set({ selectedUserId: id }),
}));

// components/UserManager.tsx — combine both
function UserManager() {
  const { data: users } = useQuery(userQueries.list());
  const { selectedUserId, setSelectedUserId } = useUiStore();
  const { data: selectedUser } = useUser(selectedUserId ?? "");

  return (
    <div className="flex gap-4">
      <UserList users={users ?? []} onSelect={setSelectedUserId} />
      {selectedUser && <UserDetail user={selectedUser} />}
    </div>
  );
}
```

---

## Testing

```tsx
// __tests__/hooks/useUsers.test.tsx
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useUsers } from "@/hooks/queries/useUsers";
import { vi } from "vitest";

function makeWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

test("fetches users successfully", async () => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve([{ id: "1", name: "Alice", email: "alice@example.com" }]),
  });

  const { result } = renderHook(() => useUsers(), { wrapper: makeWrapper() });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toHaveLength(1);
  expect(result.current.data?.[0].name).toBe("Alice");
});

test("handles error", async () => {
  global.fetch = vi.fn().mockResolvedValue({ ok: false });

  const { result } = renderHook(() => useUsers(), { wrapper: makeWrapper() });

  await waitFor(() => expect(result.current.isError).toBe(true));
  expect(result.current.error?.message).toBe("Failed to fetch users");
});
```

---

## Best Practices

```tsx
// ✅ Query factory for consistent keys
export const userQueries = { detail: (id) => queryOptions({ queryKey: ["users", id], ... }) };

// ✅ Type query functions — no `as any`
queryFn: (): Promise<User[]> => fetch("/api/users").then((r) => r.json()),

// ✅ enabled flag for conditional queries
enabled: !!userId,

// ✅ staleTime per data type
// Static config: Infinity
// User profile: 5 * 60 * 1000
// Live feed: 0

// ✅ invalidateQueries after mutation, not refetchQueries
onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] });

// ✅ placeholderData for paginated tables
placeholderData: (prev) => prev,

// ✅ Server prefetch in Next.js Server Components

// ❌ Don't store server state in Zustand
// BAD: zustand store { users: [] } fetched from API
// GOOD: useQuery for server state, zustand for UI state

// ❌ Don't use useEffect for data fetching
// BAD: useEffect(() => { fetch("/api/users").then(setUsers) }, [])
// GOOD: useQuery({ queryKey: ["users"], queryFn: fetchUsers })
```

---

## v5 Migration Notes (from v4)

| v4 | v5 |
|---|---|
| `isLoading` | `isPending` (query with no data) |
| `cacheTime` | `gcTime` |
| `useQuery(key, fn, opts)` | `useQuery({ queryKey, queryFn, ...opts })` |
| `keepPreviousData` | `placeholderData: (prev) => prev` |
| `onSuccess` in `useQuery` | `useEffect` or mutation `onSuccess` |
| `getNextPageParam` | same, but `initialPageParam` required |

---

## File Structure

```
src/
├── queries/                    # Query definitions (factory pattern)
│   ├── userQueries.ts
│   ├── orderQueries.ts
│   └── productQueries.ts
│
├── hooks/
│   ├── queries/                # useQuery wrappers
│   │   ├── useUsers.ts
│   │   └── useUser.ts
│   └── mutations/              # useMutation wrappers
│       ├── useCreateUser.ts
│       ├── useUpdateUser.ts
│       └── useDeleteUser.ts
│
├── lib/
│   └── apiClient.ts            # Axios/fetch client
│
└── app/
    └── providers.tsx           # QueryClientProvider setup
```
