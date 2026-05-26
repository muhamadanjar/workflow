# shadcn/ui Guide

Copy-paste component library built on Radix UI + Tailwind CSS.

## What is shadcn/ui?

**Not an npm package.** Copy-paste components into your project.

**Benefits:**
- Full control: copy code, modify as needed
- Tree-shakeable: only include what you use
- Composable: build complex UI from primitives
- Accessible: Radix UI primitives (WCAG 2.1)
- Styled: Tailwind CSS (dark mode included)
- Type-safe: TypeScript by default

## Installation

### 1. Initialize shadcn/ui

```bash
# CLI renamed from shadcn-ui → shadcn
npx shadcn@latest init
```

Options:
- Use TypeScript: Yes
- Which style: Default (New York)
- Base color: slate/zinc/stone/gray/neutral

Creates: `components/ui/` + `components.json` config

### 2. Add Components

```bash
# Add individual components
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
npx shadcn@latest add tabs
npx shadcn@latest add sonner   # Toast replacement

# Add all
npx shadcn@latest add --all
```

Components copied to: `src/components/ui/`

## Core Components

### Button

```tsx
import { Button } from "@/components/ui/button"

export function ButtonDemo() {
  return (
    <div className="flex gap-4">
      <Button>Default</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link">Link</Button>
      
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>
      
      <Button disabled>Disabled</Button>
      <Button disabled><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading...</Button>
    </div>
  )
}
```

### Input

```tsx
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export function InputDemo() {
  return (
    <div className="space-y-2">
      <Label htmlFor="email">Email</Label>
      <Input id="email" type="email" placeholder="name@example.com" />
      
      <Input disabled placeholder="Disabled" />
      <Input type="password" placeholder="Password" />
      <Input type="number" placeholder="Number" />
    </div>
  )
}
```

### Card

```tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function CardDemo() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
        <CardDescription>Card Description</CardDescription>
      </CardHeader>
      <CardContent>
        Card content goes here
      </CardContent>
    </Card>
  )
}
```

### Dialog

```tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

export function DialogDemo() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Dialog Title</DialogTitle>
        </DialogHeader>
        <p>Dialog content goes here</p>
      </DialogContent>
    </Dialog>
  )
}
```

### Dropdown Menu

```tsx
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"

export function DropdownMenuDemo() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">Actions</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>My Account</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem>Profile</DropdownMenuItem>
        <DropdownMenuItem>Settings</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>Logout</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### Toast (Sonner — replaces old useToast)

```bash
npx shadcn@latest add sonner
```

```tsx
// src/app/layout.tsx — add Toaster once at root
import { Toaster } from "@/components/ui/sonner"

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  )
}
```

```tsx
// Usage anywhere
import { toast } from "sonner"
import { Button } from "@/components/ui/button"

export function ToastDemo() {
  return (
    <div className="flex gap-2">
      <Button onClick={() => toast("Default message")}>Default</Button>
      <Button onClick={() => toast.success("Saved successfully")}>Success</Button>
      <Button onClick={() => toast.error("Something went wrong")}>Error</Button>
      <Button onClick={() => toast.warning("Check this out")}>Warning</Button>
      <Button onClick={() => toast.promise(saveData(), {
        loading: "Saving...",
        success: "Saved!",
        error: "Failed to save",
      })}>Promise</Button>
    </div>
  )
}
```

### Tabs

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function TabsDemo() {
  return (
    <Tabs defaultValue="account">
      <TabsList>
        <TabsTrigger value="account">Account</TabsTrigger>
        <TabsTrigger value="password">Password</TabsTrigger>
      </TabsList>
      <TabsContent value="account">Account settings</TabsContent>
      <TabsContent value="password">Password settings</TabsContent>
    </Tabs>
  )
}
```

### Form

```tsx
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"

export function FormDemo() {
  const form = useForm({
    defaultValues: {
      username: "",
      email: "",
    },
  })

  function onSubmit(values) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="john_doe" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="john@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

## Advanced Patterns

### Dark Mode Toggle

```tsx
"use client"

import { useState, useEffect } from "react"
import { Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light")

  useEffect(() => {
    const root = document.documentElement
    if (theme === "dark") {
      root.classList.add("dark")
    } else {
      root.classList.remove("dark")
    }
  }, [theme])

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
    </Button>
  )
}
```

### Custom Components (Composition)

```tsx
// components/DashboardCard.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface DashboardCardProps {
  title: string
  value: string | number
  description?: string
  icon?: React.ReactNode
}

export function DashboardCard({ title, value, description, icon }: DashboardCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </div>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  )
}

// Usage
<DashboardCard
  title="Total Sales"
  value="$45,231.89"
  description="+20.1% from last month"
  icon={<DollarSign className="h-4 w-4 text-muted-foreground" />}
/>
```

### Data Table with shadcn/ui

```tsx
"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"

export function DataTableDemo({ columns, data }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="border rounded-lg">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.map((row) => (
            <TableRow key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
```

## Best Practices

### 1. Import Organization

```typescript
// ✅ Good
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"

// ❌ Avoid
import Button from "@/components/ui/button" // Default export wrong
```

### 2. Composability

```tsx
// ✅ Good: Compose from primitives
<Card>
  <CardHeader>
    <CardTitle>Settings</CardTitle>
  </CardHeader>
  <CardContent>
    <div className="space-y-4">
      <div>
        <Label>Email</Label>
        <Input type="email" />
      </div>
      <Button>Save</Button>
    </div>
  </CardContent>
</Card>

// ❌ Avoid: Over-nesting
<Card>
  <CardHeader>
    <CardTitle>
      <span>Settings</span>
    </CardTitle>
  </CardHeader>
</Card>
```

### 3. Variant Usage

```tsx
// ✅ Correct variants
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button size="lg">Submit</Button>

// ❌ Don't style manually
<Button className="bg-red-500">Delete</Button>
```

### 4. Server vs Client Components

```tsx
// app/page.tsx (Server Component by default)
import { CardDemo } from "@/components/examples/card" // Client

export default function Page() {
  return <CardDemo />
}

// components/examples/card.tsx
"use client" // Mark for interactivity

import { Card } from "@/components/ui/card"

export function CardDemo() {
  return <Card>...</Card>
}
```

## Available Components

**Form & Input:**
- Button, Input, Label, Textarea, Checkbox, Radio Button
- Select, Combobox, Toggle, Switch
- Form (react-hook-form integration)

**Layout:**
- Card, Container, Separator
- Breadcrumb, Pagination

**Navigation:**
- Dropdown Menu, Navigation Menu, Sheet
- Tabs, Sidebar

**Overlay:**
- Dialog, Drawer, AlertDialog, Popover
- Tooltip, Context Menu

**Data:**
- Table, Data Table (with TanStack Table)

**Feedback:**
- Sonner (toast — default), Progress, Skeleton, Badge

**Charts:**
- Recharts integration (separate)

## Resources

- **Documentation:** https://ui.shadcn.com
- **Registry:** https://ui.shadcn.com/docs/components/accordion
- **GitHub:** https://github.com/shadcn-ui/ui
- **Discord Community:** https://discord.gg/pqc3wCKfms
- **Examples:** https://github.com/shadcn-ui/ui/tree/main/apps/www/app/examples

