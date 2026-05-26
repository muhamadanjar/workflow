# Next.js 16 Guide

Latest Next.js with React 19, Server Components by default, built-in optimizations.

## What's New in Next.js 16

**Key Features:**
- App Router (default)
- React Server Components (default)
- Built-in middleware
- Image optimization
- Font optimization
- Static generation + ISR
- API routes
- TypeScript by default

## Project Structure (Next.js 16)

```
myapp/
├── app/                          # App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page (/)
│   ├── error.tsx                # Error boundary
│   ├── not-found.tsx            # 404 page
│   ├── (auth)/                  # Route group (not in URL)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── dashboard/
│   │   ├── layout.tsx           # Nested layout
│   │   ├── page.tsx             # /dashboard
│   │   └── [id]/                # Dynamic route
│   │       └── page.tsx         # /dashboard/123
│   └── api/
│       ├── auth/
│       │   └── route.ts         # API endpoint
│       └── users/
│           └── [id]/
│               └── route.ts
│
├── components/
│   ├── ui/                      # shadcn/ui components
│   └── ...
│
├── lib/
│   ├── db.ts
│   ├── api.ts
│   └── utils.ts
│
├── public/                      # Static assets
├── .env.local                   # Environment variables
├── next.config.ts              # Next.js config
├── tailwind.config.ts          # Tailwind config
├── tsconfig.json               # TypeScript config
└── package.json
```

## Server vs Client Components

### Server Components (Default)

```tsx
// app/page.tsx
// This is a Server Component by default

import { UserProfile } from "@/components/user-profile"

export default async function Page() {
  // ✅ Can use async/await
  const user = await fetch(`/api/user/1`).then(r => r.json())
  
  // ✅ Can access database
  // const user = await db.user.findUnique({ where: { id: 1 } })
  
  // ✅ Can access secrets/environment variables
  // const secret = process.env.API_KEY
  
  return (
    <main>
      <h1>User Profile</h1>
      <UserProfile user={user} />
    </main>
  )
}
```

**Benefits:**
- Smaller bundle size (no JS sent to browser)
- Secure (secrets stay on server)
- Direct database access (no API layer needed)
- Single round-trip (fetch data then render)

### Client Components

```tsx
// components/user-profile.tsx
"use client"  // Mark as client component

import { useState } from "react"
import { Button } from "@/components/ui/button"

interface UserProfileProps {
  user: { id: string; name: string; email: string }
}

export function UserProfile({ user }: UserProfileProps) {
  const [isEditing, setIsEditing] = useState(false)
  
  // ✅ Can use hooks (useState, useEffect)
  // ✅ Can use browser APIs (localStorage, window)
  // ✅ Can add event listeners
  
  return (
    <div className="p-4 border rounded-lg">
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <Button onClick={() => setIsEditing(!isEditing)}>
        {isEditing ? "Done" : "Edit"}
      </Button>
    </div>
  )
}
```

**When to use:**
- Interactive features (forms, buttons, modals)
- Browser APIs (localStorage, window)
- Event listeners (onClick, onChange)
- React hooks (useState, useEffect)

### Mixing Server & Client

```tsx
// ✅ Good: Server fetches data, client shows UI
// app/posts/page.tsx (Server Component)
import { PostCard } from "@/components/post-card"

export default async function PostsPage() {
  const posts = await fetch(`/api/posts`).then(r => r.json())
  
  return (
    <div className="grid gap-4">
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  )
}

// components/post-card.tsx (Client Component)
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

interface PostCardProps {
  post: { id: string; title: string; content: string }
}

export function PostCard({ post }: PostCardProps) {
  const [liked, setLiked] = useState(false)
  
  return (
    <div className="p-4 border rounded-lg">
      <h3>{post.title}</h3>
      <p>{post.content}</p>
      <Button
        variant={liked ? "default" : "outline"}
        onClick={() => setLiked(!liked)}
      >
        {liked ? "❤️" : "🤍"} Like
      </Button>
    </div>
  )
}
```

## Routing Patterns

### Dynamic Routes

> **Next.js 15+ breaking change:** `params` and `searchParams` are now `Promise`. Must `await` them.

```tsx
// app/posts/[id]/page.tsx
interface PostPageProps {
  params: Promise<{ id: string }>
  searchParams: Promise<{ view?: string }>
}

export default async function PostPage({ params, searchParams }: PostPageProps) {
  const { id } = await params
  const { view } = await searchParams

  return (
    <div>
      <h1>Post {id}</h1>
      {view === "full" && <p>Full view</p>}
    </div>
  )
}

// Generates static params (for optimization)
export async function generateStaticParams() {
  const posts = await fetch(`/api/posts`).then(r => r.json())
  return posts.map(post => ({ id: post.id }))
}
```

### Nested Routes & Layouts

```tsx
// app/dashboard/layout.tsx
import { Sidebar } from "@/components/sidebar"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1">{children}</main>
    </div>
  )
}

// app/dashboard/page.tsx (inherits layout)
export default function DashboardPage() {
  return <h1>Dashboard</h1>
}

// app/dashboard/settings/page.tsx (also inherits layout)
export default function SettingsPage() {
  return <h1>Settings</h1>
}
```

### Route Groups (No URL impact)

```
app/
├── (auth)/
│   ├── layout.tsx          # Auth layout (different from main)
│   ├── login/page.tsx      # /login
│   └── register/page.tsx   # /register
├── (marketing)/
│   ├── layout.tsx          # Marketing layout
│   ├── about/page.tsx      # /about
│   └── pricing/page.tsx    # /pricing
└── dashboard/
    ├── layout.tsx          # Dashboard layout
    └── page.tsx            # /dashboard
```

## API Routes

```typescript
// app/api/posts/route.ts
export async function GET(request: Request) {
  // GET /api/posts
  const posts = await db.post.findMany()
  return Response.json(posts)
}

export async function POST(request: Request) {
  // POST /api/posts
  const body = await request.json()
  const post = await db.post.create({ data: body })
  return Response.json(post, { status: 201 })
}

// app/api/posts/[id]/route.ts
export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  // GET /api/posts/123
  const { id } = await params
  const post = await db.post.findUnique({ where: { id } })
  return Response.json(post)
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  // PUT /api/posts/123
  const { id } = await params
  const body = await request.json()
  const post = await db.post.update({ where: { id }, data: body })
  return Response.json(post)
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  // DELETE /api/posts/123
  const { id } = await params
  await db.post.delete({ where: { id } })
  return new Response(null, { status: 204 })
}
```

## Middleware

```typescript
// middleware.ts (root)
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  // Check authentication
  const token = request.cookies.get("token")?.value
  
  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ["/dashboard/:path*", "/api/protected/:path*"],
}
```

## Data Fetching Patterns

### Server Component with Direct Fetch

```tsx
// app/posts/page.tsx
export default async function PostsPage() {
  const posts = await fetch(`${process.env.API_URL}/posts`, {
    next: { revalidate: 60 }  // ISR: revalidate every 60 seconds
  }).then(r => r.json())
  
  return (
    <div>
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  )
}
```

### Incremental Static Regeneration (ISR)

```tsx
// app/posts/page.tsx
export const revalidate = 60  // Revalidate every 60 seconds

export default async function PostsPage() {
  const posts = await fetch(`/api/posts`, {
    next: { revalidate: 60 }
  }).then(r => r.json())
  
  return <div>{/* ... */}</div>
}
```

### Client Component with useEffect

```tsx
"use client"

import { useEffect, useState } from "react"

export function PostsList() {
  const [posts, setPosts] = useState([])
  
  useEffect(() => {
    fetch("/api/posts")
      .then(r => r.json())
      .then(data => setPosts(data))
  }, [])
  
  return <div>{/* ... */}</div>
}
```

## Optimizations

### Image Optimization

```tsx
import Image from "next/image"

export function HeroImage() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero"
      width={1200}
      height={600}
      priority  // Load immediately (LCP image)
      sizes="(max-width: 768px) 100vw, 50vw"
    />
  )
}
```

### Font Optimization

```tsx
// app/layout.tsx
import { Inter, Playfair_Display } from "next/font/google"

const inter = Inter({ subsets: ["latin"] })
const playfair = Playfair_Display({ subsets: ["latin"] })

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.className}>
      <body>
        <h1 className={playfair.className}>Title</h1>
        {children}
      </body>
    </html>
  )
}
```

### Dynamic Imports

```tsx
import dynamic from "next/dynamic"

const HeavyComponent = dynamic(
  () => import("@/components/heavy-component"),
  { loading: () => <p>Loading...</p> }
)

export function Page() {
  return <HeavyComponent />
}
```

## Environment Variables

```bash
# .env.local
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=secret_key
NEXT_PUBLIC_API_URL=https://api.example.com  # Public in browser
```

```typescript
// Usage in server component
const dbUrl = process.env.DATABASE_URL  // ✅ Only on server

// Usage in client component
const apiUrl = process.env.NEXT_PUBLIC_API_URL  // ✅ Available in browser
```

## Best Practices

✅ **Default to Server Components**
- Fetch data server-side
- Keep heavy logic on server
- Send only rendered HTML to client

✅ **Use "use client" Sparingly**
- Push "use client" to leaves (specific components)
- Server component can contain client component
- But client component cannot contain server component

✅ **Organize Routes Logically**
- Use route groups for layout variants
- Nested layouts for shared UI
- Dynamic segments for content

✅ **Leverage Next.js Optimizations**
- Image optimization (next/image)
- Font optimization (next/font)
- Code splitting (dynamic imports)
- Caching strategies (cache, revalidate)

✅ **Type-Safe Parameters (Next.js 15+)**
```tsx
// ✅ params and searchParams are Promise in Next.js 15+
interface PageProps {
  params: Promise<{ id: string }>
  searchParams: Promise<Record<string, string>>
}

export default async function Page({ params, searchParams }: PageProps) {
  const { id } = await params
  const { filter } = await searchParams
}
```

## Resources

- **Documentation:** https://nextjs.org
- **App Router:** https://nextjs.org/docs/app
- **API Reference:** https://nextjs.org/docs/app/api-reference
- **Examples:** https://github.com/vercel/next.js/tree/canary/examples
- **Vercel Deployment:** https://vercel.com

