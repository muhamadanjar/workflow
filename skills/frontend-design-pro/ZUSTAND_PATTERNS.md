# Zustand Patterns & Best Practices

Production-ready Zustand patterns for React/Next.js applications.

## Table of Contents

1. [Basic Store](#basic-store)
2. [Middleware](#middleware)
3. [Advanced Patterns](#advanced-patterns)
4. [Performance](#performance)
5. [Testing](#testing)

---

## Basic Store

### Simple Store
```typescript
import { create } from "zustand";

interface CounterStore {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

export const useCounterStore = create<CounterStore>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}));
```

### Store with Async Actions
```typescript
interface UserStore {
  user: User | null;
  loading: boolean;
  error: string | null;
  fetchUser: (id: string) => Promise<void>;
}

export const useUserStore = create<UserStore>((set) => ({
  user: null,
  loading: false,
  error: null,

  fetchUser: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`/api/users/${id}`);
      if (!response.ok) throw new Error("Failed to fetch");
      const user = await response.json();
      set({ user, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Unknown error",
        loading: false,
      });
    }
  },
}));
```

---

## Middleware

### Persist Middleware (localStorage)
```typescript
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthStore {
  token: string | null;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      token: null,
      setToken: (token: string) => set({ token }),
    }),
    {
      name: "auth-storage", // localStorage key
      partialize: (state) => ({ token: state.token }), // Only persist these
    }
  )
);
```

### Immer Middleware (Immutable Updates)
```typescript
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

interface TodoStore {
  todos: Todo[];
  addTodo: (todo: Todo) => void;
  updateTodo: (id: string, updates: Partial<Todo>) => void;
  removeTodo: (id: string) => void;
}

export const useTodoStore = create<TodoStore>()(
  immer((set) => ({
    todos: [],
    addTodo: (todo) =>
      set((state) => {
        state.todos.push(todo);
      }),
    updateTodo: (id, updates) =>
      set((state) => {
        const todo = state.todos.find((t) => t.id === id);
        if (todo) Object.assign(todo, updates);
      }),
    removeTodo: (id) =>
      set((state) => {
        state.todos = state.todos.filter((t) => t.id !== id);
      }),
  }))
);
```

### DevTools Middleware (Debugging)
```typescript
import { create } from "zustand";
import { devtools } from "zustand/middleware";

export const useAppStore = create<AppStore>()(
  devtools((set) => ({
    // ...
  }), {
    name: "app-store",
    trace: true,
  })
);
```

### Combining Multiple Middleware
```typescript
import { create } from "zustand";
import { persist, devtools } from "zustand/middleware";

export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      (set) => ({
        // store definition
      }),
      { name: "app-storage" }
    ),
    { name: "app-store" }
  )
);
```

---

## Advanced Patterns

### Store with Selectors
```typescript
interface UserStore {
  user: User | null;
  preferences: Preferences;
  // ... state
}

export const useUserStore = create<UserStore>(/* ... */);

// Selectors for efficiency
export const selectUser = (state: UserStore) => state.user;
export const selectUserEmail = (state: UserStore) => state.user?.email;
export const selectPreferences = (state: UserStore) => state.preferences;

// Usage (only re-renders when selected value changes)
function Profile() {
  const email = useUserStore(selectUserEmail);
  return <div>{email}</div>;
}
```

### Slice Pattern (Multiple Stores)
```typescript
// stores/auth.ts
export interface AuthSlice {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

export const createAuthSlice = (set: SetState<AppStore>): AuthSlice => ({
  user: null,
  login: async (credentials) => {
    const user = await api.login(credentials);
    set({ user });
  },
  logout: () => set({ user: null }),
});

// stores/ui.ts
export interface UISlice {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const createUISlice = (set: SetState<AppStore>): UISlice => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
});

// stores/index.ts
import { create } from "zustand";
import { AuthSlice, createAuthSlice } from "./auth";
import { UISlice, createUISlice } from "./ui";

export type AppStore = AuthSlice & UISlice;

export const useAppStore = create<AppStore>((set) => ({
  ...createAuthSlice(set),
  ...createUISlice(set),
}));
```

### Async Factory Pattern
```typescript
interface UserStore {
  users: User[];
  isLoading: boolean;
  error: string | null;
  fetchUsers: () => Promise<void>;
}

export const useUserStore = create<UserStore>((set) => ({
  users: [],
  isLoading: false,
  error: null,

  fetchUsers: async () => {
    set({ isLoading: true });
    try {
      const response = await fetch("/api/users");
      const users = await response.json();
      set({ users, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Unknown error",
        isLoading: false,
      });
    }
  },
}));

// React component
function UserList() {
  const { users, isLoading, error, fetchUsers } = useUserStore();

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### Conditional State Updates
```typescript
const updateUser = (updates: Partial<User>) => {
  set((state) => {
    // Only update if validation passes
    if (updates.email && !isValidEmail(updates.email)) {
      return state;
    }
    return { user: { ...state.user, ...updates } };
  });
};
```

---

## Performance

### Selector Hook to Prevent Re-renders
```typescript
// ❌ BAD - Re-renders on any state change
function Component() {
  const store = useUserStore(); // Subscribes to entire store
  return <div>{store.user?.name}</div>;
}

// ✅ GOOD - Only re-renders when user changes
function Component() {
  const userName = useUserStore((state) => state.user?.name);
  return <div>{userName}</div>;
}

// ✅ BETTER - Create selector function
const selectUserName = (state: UserStore) => state.user?.name;

function Component() {
  const userName = useUserStore(selectUserName);
  return <div>{userName}</div>;
}
```

### Shallow Comparison
```typescript
import { shallow } from "zustand/react/shallow";

// Only re-render if user OR preferences change
const { user, preferences } = useUserStore(
  (state) => ({ user: state.user, preferences: state.preferences }),
  shallow
);
```

### useShallow Hook (React 19+)
```typescript
import { useShallow } from "zustand/react/useShallow";

const { user, preferences } = useUserStore(
  useShallow((state) => ({
    user: state.user,
    preferences: state.preferences,
  }))
);
```

---

## Testing

### Unit Testing Store
```typescript
// __tests__/stores/authStore.test.ts
import { renderHook, act } from "@testing-library/react";
import { useAuthStore } from "@/stores/authStore";

describe("useAuthStore", () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.setState({ token: null, user: null });
  });

  test("login sets token and user", async () => {
    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.login("test@example.com", "password");
    });

    expect(result.current.token).toBeDefined();
    expect(result.current.user?.email).toBe("test@example.com");
  });

  test("logout clears state", () => {
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.logout();
    });

    expect(result.current.token).toBeNull();
    expect(result.current.user).toBeNull();
  });
});
```

### Integration Testing with Components
```typescript
// __tests__/components/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { LoginForm } from "@/components/forms/LoginForm";
import { useAuthStore } from "@/stores/authStore";

test("login form submits credentials", async () => {
  const mockLogin = jest.fn();
  useAuthStore.setState({ login: mockLogin });

  render(<LoginForm />);

  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: "test@example.com" },
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: "password" },
  });
  fireEvent.click(screen.getByRole("button", { name: /login/i }));

  await waitFor(() => {
    expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password");
  });
});
```

---

## Anti-Patterns

### ❌ Mutating State Directly
```typescript
// WRONG
increment: () => {
  const state = get();
  state.count++; // Direct mutation!
},

// CORRECT
increment: () => set((state) => ({ count: state.count + 1 })),
```

### ❌ Too Large Store
```typescript
// WRONG - Store too large, mixing concerns
create((set) => ({
  user: null,
  theme: "light",
  notifications: [],
  cart: [],
  orders: [],
  // ... 50 more fields
}));

// CORRECT - Split into smaller stores
useAuthStore, useThemeStore, useCartStore, useNotificationStore
```

### ❌ Duplicating Store in Multiple Components
```typescript
// WRONG
function Component1() {
  const store = useUserStore();
}

function Component2() {
  const store = useUserStore(); // Duplicate subscriptions
}

// CORRECT - Create selector functions
function Component1() {
  const userName = useUserStore((state) => state.user?.name);
}

function Component2() {
  const userEmail = useUserStore((state) => state.user?.email);
}
```

---

## Common Patterns

### Form State Management
```typescript
interface FormStore {
  values: Record<string, any>;
  errors: Record<string, string>;
  isDirty: boolean;
  isSubmitting: boolean;
  setFieldValue: (name: string, value: any) => void;
  setFieldError: (name: string, error: string) => void;
  reset: () => void;
  submit: (onSubmit: Function) => Promise<void>;
}

export const useFormStore = create<FormStore>((set, get) => ({
  values: {},
  errors: {},
  isDirty: false,
  isSubmitting: false,

  setFieldValue: (name, value) =>
    set((state) => ({
      values: { ...state.values, [name]: value },
      isDirty: true,
    })),

  setFieldError: (name, error) =>
    set((state) => ({
      errors: { ...state.errors, [name]: error },
    })),

  reset: () =>
    set({ values: {}, errors: {}, isDirty: false, isSubmitting: false }),

  submit: async (onSubmit) => {
    set({ isSubmitting: true });
    try {
      await onSubmit(get().values);
      set({ isSubmitting: false, isDirty: false });
    } catch (error) {
      set({ isSubmitting: false });
    }
  },
}));
```

### Notification/Toast Store
```typescript
interface Notification {
  id: string;
  message: string;
  type: "success" | "error" | "info" | "warning";
  duration?: number;
}

interface NotificationStore {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, "id">) => void;
  removeNotification: (id: string) => void;
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  notifications: [],

  addNotification: ({ message, type, duration = 3000 }) => {
    const id = Math.random().toString(36).substr(2, 9);
    set((state) => ({
      notifications: [...state.notifications, { id, message, type }],
    }));

    if (duration > 0) {
      setTimeout(() => {
        useNotificationStore.getState().removeNotification(id);
      }, duration);
    }
  },

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
}));
```

---

## Tips & Tricks

1. **Use `get()` for non-reactive updates:**
   ```typescript
   const count = useStore.getState().count; // No subscription
   ```

2. **Combine stores with custom hooks:**
   ```typescript
   export function useUser() {
     const user = useUserStore((state) => state.user);
     const preferences = usePreferencesStore((state) => state.preferences);
     return { user, preferences };
   }
   ```

3. **Async initialization:**
   ```typescript
   useAuthStore.subscribe(
     (state) => state.token,
     async (token) => {
       if (token) await initializeApp();
     }
   );
   ```

4. **State reset between tests:**
   ```typescript
   const initialState = useAuthStore.getState();
   useAuthStore.setState(initialState);
   ```
