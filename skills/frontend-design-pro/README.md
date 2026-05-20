# Frontend Design Pro - Tailwind CSS v4 + MUI + Zustand

Professional frontend design skill: Modern UI components, state management, and design patterns for React/Next.js.

## Tech Stack

- **UI Framework:** Next.js 14+ (React 19+)
- **Styling:** Tailwind CSS v4 (latest)
- **Component Library:** Material-UI (MUI) v6
- **State Management:** Zustand (lightweight, TypeScript-first)
- **Type Safety:** TypeScript (strict mode)

## What's Included

### 1. Component Library
- Pre-built, production-ready components
- Fully typed with TypeScript
- Tailwind CSS + MUI integration
- Dark mode support
- Accessibility (a11y) built-in

### 2. Store Patterns (Zustand)
- Global state management
- Middleware examples (persist, devtools)
- Async actions
- Selectors for performance
- TypeScript generics

### 3. Design System
- Tailwind config (colors, typography, spacing)
- CSS-in-JS patterns
- Component composition patterns
- Layout components

### 4. Templates & Examples
- Authentication (login/register)
- Dashboard layout
- Data table with pagination
- Form validation
- Modal dialogs
- Toast notifications

### 5. Best Practices
- Separation of concerns
- Custom hooks
- Error boundaries
- Performance optimization
- Testing patterns

## Project Structure

```
src/
├── components/
│   ├── ui/                    # Reusable UI components
│   │   ├── Button.tsx         # Button (Tailwind)
│   │   ├── Card.tsx           # Card (Tailwind)
│   │   ├── Modal.tsx          # Modal (MUI)
│   │   ├── TextField.tsx       # Input (MUI)
│   │   └── Badge.tsx          # Badge (Tailwind + MUI)
│   ├── forms/                 # Form components
│   │   ├── LoginForm.tsx      # Login (MUI + Zustand)
│   │   ├── RegisterForm.tsx   # Register
│   │   └── ProfileForm.tsx    # Profile edit
│   ├── layouts/               # Layout components
│   │   ├── MainLayout.tsx     # Main layout
│   │   ├── AuthLayout.tsx     # Auth pages layout
│   │   └── DashboardLayout.tsx
│   └── common/                # Shared components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
│
├── stores/                    # Zustand stores (state)
│   ├── authStore.ts           # Auth state
│   ├── userStore.ts           # User profile state
│   ├── uiStore.ts             # UI state (modals, notifications)
│   └── middleware/
│       ├── persist.ts         # Persist state to localStorage
│       └── logger.ts          # DevTools logging
│
├── hooks/                     # Custom React hooks
│   ├── useAuth.ts             # Auth hook
│   ├── useForm.ts             # Form validation
│   ├── useLocalStorage.ts     # Local storage hook
│   └── useMediaQuery.ts       # Responsive hook
│
├── styles/                    # Global styles
│   ├── globals.css            # Tailwind directives
│   └── tailwind.config.ts     # Tailwind config
│
├── types/                     # TypeScript definitions
│   ├── auth.ts
│   ├── user.ts
│   └── api.ts
│
├── utils/                     # Utilities
│   ├── cn.ts                  # Class name merge (Tailwind)
│   ├── api.ts                 # API client
│   └── validation.ts          # Form validation
│
├── app/                       # Next.js app router
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Home page
│   ├── (auth)/                # Auth route group
│   │   ├── login/
│   │   └── register/
│   └── dashboard/
│       ├── page.tsx
│       └── [id]/
│
└── __tests__/                 # Tests
    ├── components/
    ├── hooks/
    └── stores/
```

## Key Technologies

### Tailwind CSS v4
Latest version with built-in CSS nesting, improved @apply, and performance.

```css
/* globals.css */
@import "tailwindcss";

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700;
  }
}
```

### MUI v6
Pre-built Material Design components.

```tsx
import { Button, TextField, Stack } from "@mui/material";

export function LoginForm() {
  return (
    <Stack spacing={2}>
      <TextField label="Email" type="email" />
      <Button variant="contained">Login</Button>
    </Stack>
  );
}
```

### Zustand
Lightweight, type-safe state management.

```typescript
import { create } from "zustand";

interface AuthStore {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  login: async (email, password) => {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    set({ user: data.user, token: data.token });
  },
  logout: () => set({ user: null, token: null }),
}));
```

## Component Examples

### Button Component (Tailwind)
```tsx
// components/ui/Button.tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export function Button({
  variant = "primary",
  size = "md",
  isLoading = false,
  children,
  ...props
}: ButtonProps) {
  const baseStyles = "font-medium rounded-lg transition-colors focus:outline-none focus:ring-2";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500",
    outline: "border-2 border-blue-600 text-blue-600 hover:bg-blue-50",
  };
  const sizes = {
    sm: "px-3 py-1 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]}`}
      disabled={isLoading}
      {...props}
    >
      {isLoading ? "Loading..." : children}
    </button>
  );
}
```

### Form Component (MUI + Zustand)
```tsx
// components/forms/LoginForm.tsx
import { useState } from "react";
import { TextField, Button, Stack, Alert } from "@mui/material";
import { useAuthStore } from "@/stores/authStore";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const login = useAuthStore((state) => state.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Stack spacing={2}>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          fullWidth
          required
        />
        <TextField
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
          required
        />
        <Button variant="contained" type="submit" fullWidth>
          Login
        </Button>
      </Stack>
    </form>
  );
}
```

### Store (Zustand)
```typescript
// stores/authStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
          });

          if (!response.ok) throw new Error("Login failed");

          const data = await response.json();
          set({ user: data.user, token: data.token, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : "Unknown error",
            isLoading: false,
          });
        }
      },

      logout: () => set({ user: null, token: null }),
      setUser: (user) => set({ user }),
    }),
    {
      name: "auth-storage", // localStorage key
      partialize: (state) => ({ user: state.user, token: state.token }), // Only persist these fields
    }
  )
);
```

## Setup

### 1. Create Next.js Project
```bash
npx create-next-app@latest myapp --typescript --tailwind
cd myapp
```

### 2. Install Dependencies
```bash
npm install zustand @mui/material @emotion/react @emotion/styled
npm install -D tailwindcss postcss autoprefixer
```

### 3. Configure Tailwind CSS v4
```javascript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563eb',
        secondary: '#64748b',
      },
    },
  },
  plugins: [],
}
export default config
```

### 4. Global Styles
```css
/* src/styles/globals.css */
@import "tailwindcss";

@layer base {
  body {
    @apply bg-white text-gray-900 dark:bg-gray-900 dark:text-white;
  }
}

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700;
  }
  
  .card {
    @apply bg-white dark:bg-gray-800 rounded-lg shadow-md p-6;
  }
}
```

## Common Patterns

### Custom Hook with Store
```typescript
// hooks/useAuth.ts
import { useAuthStore } from "@/stores/authStore";

export function useAuth() {
  const user = useAuthStore((state) => state.user);
  const token = useAuthStore((state) => state.token);
  const logout = useAuthStore((state) => state.logout);
  const isAuthenticated = !!user && !!token;

  return { user, token, logout, isAuthenticated };
}

// Usage
function Profile() {
  const { user, logout } = useAuth();
  return <div>{user?.name} <button onClick={logout}>Logout</button></div>;
}
```

### Form Validation Hook
```typescript
// hooks/useForm.ts
import { useState } from "react";

export function useForm<T>(initialValues: T, onSubmit: (values: T) => Promise<void>) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Partial<T>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } finally {
      setIsSubmitting(false);
    }
  };

  return { values, errors, isSubmitting, handleChange, handleSubmit };
}
```

### Reusable Card Component (Tailwind + TypeScript)
```tsx
// components/ui/Card.tsx
interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function Card({ title, children, className = "" }: CardProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 ${className}`}>
      {title && <h2 className="text-xl font-bold mb-4">{title}</h2>}
      {children}
    </div>
  );
}
```

## Best Practices

### 1. Component Composition
```tsx
// Good: Small, composable components
<Card title="User Profile">
  <Stack spacing={2}>
    <TextField label="Name" />
    <Button>Save</Button>
  </Stack>
</Card>
```

### 2. Selective Store Subscriptions
```typescript
// ✅ Efficient - only subscribes to email
const email = useAuthStore((state) => state.user?.email);

// ❌ Inefficient - re-renders on any store change
const state = useAuthStore();
```

### 3. Type-Safe API Calls
```typescript
// types/api.ts
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
}

// stores/authStore.ts
const response = await fetch("/api/auth/login");
const data: LoginResponse = await response.json();
```

### 4. Dark Mode Support
```tsx
// Tailwind handles dark mode
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Content
</div>
```

## File Structure Details

### Components
- Keep components small and focused
- One component per file
- Export component and types
- Use TypeScript interfaces for props

### Stores
- One store per feature (auth, user, ui)
- Use middleware for persistence/logging
- Selector functions for optimization
- Proper error handling

### Hooks
- Reusable logic extraction
- Combine stores with logic
- Custom form, fetch, validation hooks

## Testing

### Component Testing
```typescript
// __tests__/components/Button.test.tsx
import { render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/Button";

test("renders button with text", () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText("Click me")).toBeInTheDocument();
});
```

### Store Testing
```typescript
// __tests__/stores/authStore.test.ts
import { renderHook, act } from "@testing-library/react";
import { useAuthStore } from "@/stores/authStore";

test("login updates user", async () => {
  const { result } = renderHook(() => useAuthStore());
  await act(async () => {
    await result.current.login("test@example.com", "password");
  });
  expect(result.current.user).toBeDefined();
});
```

## Resources

- **Tailwind CSS:** https://tailwindcss.com
- **MUI Docs:** https://mui.com
- **Zustand:** https://github.com/pmndrs/zustand
- **Next.js:** https://nextjs.org
- **React Docs:** https://react.dev

## Quick Start

```bash
# See SETUP_GUIDE.md for detailed setup
# Copy templates from templates/ directory
# Review examples in examples/ directory
```
