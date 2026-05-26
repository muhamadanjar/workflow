# Material-UI (MUI) v9 Guide

> **MUI v9** is current stable. Breaking changes from v5→v6: Grid new API (`size` prop, no `item`). From v6+: CSS Variables theming. Check [migration guide](https://mui.com/material-ui/migration/) for v6→v9 specifics.

Pre-built Material Design components for React/Next.js.

## What is MUI?

**Complete component library** with pre-built Material Design components.

**vs shadcn/ui:**
| Aspect | MUI | shadcn/ui |
|--------|-----|-----------|
| Format | npm package | copy-paste |
| Customization | Theme system | Direct code modification |
| Bundle size | Larger | Smaller (only what you use) |
| Styling | Emotion or Pigment CSS | Tailwind CSS |
| Pre-built | Yes, opinionated | Yes, copy-paste |
| Learning curve | Steeper (theme system) | Easier |
| Dark mode | Built-in | Built-in |
| TypeScript | Full support | Full support |

**When to choose MUI:**
- Want complete design system
- Need Material Design
- Prefer npm package (easier updates)
- Want pre-configured theming
- Working with complex data visualization

## Installation

```bash
# Create Next.js project
npx create-next-app@latest myapp --typescript --app

# Install MUI v9
npm install @mui/material@9 @emotion/react @emotion/styled

# Install icons
npm install @mui/icons-material@9

# Optional: MUI X — check https://mui.com/x/introduction/installation/ for version that pairs with MUI v9
npm install @mui/x-data-grid @mui/x-date-pickers
```

## Core Imports

```typescript
// Components
import { Button, TextField, Card, Dialog } from "@mui/material"

// Icons
import DeleteIcon from "@mui/icons-material/Delete"
import EditIcon from "@mui/icons-material/Edit"

// Layout
import { Stack, Box, Container, Grid } from "@mui/material"

// Theme
import { createTheme, ThemeProvider } from "@mui/material/styles"
```

## Basic Setup

### 1. Create Theme

```typescript
// src/lib/theme.ts
import { createTheme } from "@mui/material/styles"

export const lightTheme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#2563eb",
    },
    secondary: {
      main: "#64748b",
    },
    background: {
      default: "#f8fafc",
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
    h1: {
      fontSize: "2.5rem",
      fontWeight: 700,
    },
  },
})

export const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#60a5fa",
    },
    secondary: {
      main: "#94a3b8",
    },
    background: {
      default: "#0f172a",
    },
  },
})

// v6: CSS Variables theme (recommended — avoids flash of unstyled content)
import { extendTheme } from "@mui/material/styles"

export const cssVarsTheme = extendTheme({
  colorSchemes: {
    light: {
      palette: {
        primary: { main: "#2563eb" },
        background: { default: "#f8fafc" },
      },
    },
    dark: {
      palette: {
        primary: { main: "#60a5fa" },
        background: { default: "#0f172a" },
      },
    },
  },
})
```

### 2. Setup Root Layout

```tsx
// src/app/layout.tsx — using CSS Variables theme (v6, recommended)
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter"
import { CssVarsProvider } from "@mui/material/styles"
import CssBaseline from "@mui/material/CssBaseline"
import { cssVarsTheme } from "@/lib/theme"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <AppRouterCacheProvider>
          <CssVarsProvider theme={cssVarsTheme}>
            <CssBaseline />
            {children}
          </CssVarsProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  )
}
```

```bash
# Required for Next.js App Router + MUI v9
npm install @mui/material-nextjs@9
```

```tsx
// Alternative: classic ThemeProvider (still works)
"use client"

import { ThemeProvider } from "@mui/material/styles"
import CssBaseline from "@mui/material/CssBaseline"
import { useState } from "react"
import { lightTheme, darkTheme } from "@/lib/theme"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [darkMode, setDarkMode] = useState(false)

  return (
    <html lang="en">
      <body>
        <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

## Core Components

### Button

```tsx
import { Button, Stack } from "@mui/material"

export function ButtonDemo() {
  return (
    <Stack direction="row" spacing={2}>
      {/* Variants */}
      <Button variant="contained">Contained</Button>
      <Button variant="outlined">Outlined</Button>
      <Button variant="text">Text</Button>
      
      {/* Colors */}
      <Button color="primary">Primary</Button>
      <Button color="secondary">Secondary</Button>
      <Button color="error">Error</Button>
      <Button color="success">Success</Button>
      
      {/* Sizes */}
      <Button size="small">Small</Button>
      <Button size="medium">Medium</Button>
      <Button size="large">Large</Button>
      
      {/* States */}
      <Button disabled>Disabled</Button>
      <Button loading>Loading</Button>
      
      {/* Full width */}
      <Button fullWidth>Full Width</Button>
    </Stack>
  )
}
```

### TextField (Input)

```tsx
import { TextField, Stack } from "@mui/material"

export function TextFieldDemo() {
  return (
    <Stack spacing={2} sx={{ width: 300 }}>
      {/* Basic */}
      <TextField label="Standard" />
      <TextField label="Outlined" variant="outlined" />
      <TextField label="Filled" variant="filled" />
      
      {/* Types */}
      <TextField label="Email" type="email" />
      <TextField label="Password" type="password" />
      <TextField label="Number" type="number" />
      
      {/* States */}
      <TextField label="With helper text" helperText="This is a helper text" />
      <TextField label="Error" error helperText="This is an error" />
      <TextField label="Disabled" disabled />
      
      {/* Multiline */}
      <TextField label="Multiline" multiline rows={4} />
      
      {/* Validation */}
      <TextField
        label="Required"
        required
        error={!value}
        helperText={!value ? "This field is required" : ""}
      />
    </Stack>
  )
}
```

### Card

```tsx
import {
  Card,
  CardActions,
  CardContent,
  CardMedia,
  Button,
  Typography,
} from "@mui/material"

export function CardDemo() {
  return (
    <Card sx={{ maxWidth: 345 }}>
      <CardMedia
        component="img"
        height="140"
        image="/image.jpg"
        alt="green iguana"
      />
      <CardContent>
        <Typography gutterBottom variant="h5" component="div">
          Card Title
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Card content goes here
        </Typography>
      </CardContent>
      <CardActions>
        <Button size="small">Share</Button>
        <Button size="small">Learn More</Button>
      </CardActions>
    </Card>
  )
}
```

### Dialog

```tsx
import { Dialog, DialogTitle, DialogContent, DialogActions, Button } from "@mui/material"
import { useState } from "react"

export function DialogDemo() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button onClick={() => setOpen(true)}>Open Dialog</Button>
      
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Dialog Title</DialogTitle>
        <DialogContent>
          Dialog content goes here
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={() => setOpen(false)} variant="contained">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}
```

### Menu & Dropdown

```tsx
import { Button, Menu, MenuItem } from "@mui/material"
import { useState } from "react"

export function MenuDemo() {
  const [anchorEl, setAnchorEl] = useState(null)
  const open = Boolean(anchorEl)

  return (
    <>
      <Button onClick={(e) => setAnchorEl(e.currentTarget)}>
        Actions
      </Button>
      
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={() => setAnchorEl(null)}>Profile</MenuItem>
        <MenuItem onClick={() => setAnchorEl(null)}>Settings</MenuItem>
        <MenuItem onClick={() => setAnchorEl(null)}>Logout</MenuItem>
      </Menu>
    </>
  )
}
```

### Tabs

```tsx
import { Tabs, Tab, Box } from "@mui/material"
import { useState } from "react"

export function TabsDemo() {
  const [value, setValue] = useState(0)

  return (
    <Box sx={{ width: "100%" }}>
      <Tabs value={value} onChange={(_, newValue) => setValue(newValue)}>
        <Tab label="Tab 1" />
        <Tab label="Tab 2" />
        <Tab label="Tab 3" />
      </Tabs>
      
      <Box sx={{ p: 2 }}>
        {value === 0 && <div>Content 1</div>}
        {value === 1 && <div>Content 2</div>}
        {value === 2 && <div>Content 3</div>}
      </Box>
    </Box>
  )
}
```

### Alert & Snackbar

```tsx
import { Alert, Snackbar } from "@mui/material"
import { useState } from "react"

export function AlertDemo() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Snackbar
        open={open}
        autoHideDuration={6000}
        onClose={() => setOpen(false)}
      >
        <Alert severity="success" onClose={() => setOpen(false)}>
          Success message!
        </Alert>
      </Snackbar>
    </>
  )
}
```

## Layout Components

### Stack (Flexbox)

```tsx
import { Stack, Button } from "@mui/material"

// Row layout
<Stack direction="row" spacing={2}>
  <Button>Button 1</Button>
  <Button>Button 2</Button>
</Stack>

// Column layout (default)
<Stack spacing={2}>
  <Button>Button 1</Button>
  <Button>Button 2</Button>
</Stack>

// Responsive
<Stack direction={{ xs: "column", md: "row" }} spacing={2}>
  <div>Mobile: column, Desktop: row</div>
</Stack>
```

### Grid (v6 — breaking change from v5)

v6 removes `item` prop and `xs`/`sm`/`md` direct props. Use `size` instead.

```tsx
import { Grid } from "@mui/material"

// ✅ v6 syntax
<Grid container spacing={2}>
  <Grid size={{ xs: 12, sm: 6, md: 4 }}>
    <div>Item 1</div>
  </Grid>
  <Grid size={{ xs: 12, sm: 6, md: 4 }}>
    <div>Item 2</div>
  </Grid>
  <Grid size={{ xs: 12, sm: 6, md: 4 }}>
    <div>Item 3</div>
  </Grid>
</Grid>

// Fixed size
<Grid size={6}>Fixed half width</Grid>

// Auto size (fills remaining space)
<Grid size="grow">Grow</Grid>

// ❌ OLD v5 syntax — do not use
// <Grid item xs={12} sm={6}>
```

### Box

```tsx
import { Box } from "@mui/material"

// Custom styling with sx prop
<Box
  sx={{
    width: "100%",
    padding: 2,
    backgroundColor: "primary.light",
    borderRadius: 1,
  }}
>
  Content
</Box>
```

## Form Handling

### Basic Form with useState

```tsx
"use client"

import { TextField, Button, Stack, Alert } from "@mui/material"
import { useState } from "react"

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) throw new Error("Login failed")
      
      const data = await response.json()
      // Handle success
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Stack spacing={2} sx={{ maxWidth: 400 }}>
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
      
      <Button
        variant="contained"
        type="submit"
        onClick={handleSubmit}
        loading={loading}
        fullWidth
      >
        Sign In
      </Button>
    </Stack>
  )
}
```

### Form with react-hook-form

```bash
npm install react-hook-form
```

```tsx
"use client"

import { useForm, Controller } from "react-hook-form"
import { TextField, Button, Stack, Alert } from "@mui/material"

export function RegistrationForm() {
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
    },
  })

  const onSubmit = async (data) => {
    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    
    if (response.ok) {
      // Handle success
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Stack spacing={2}>
        <Controller
          name="email"
          control={control}
          rules={{
            required: "Email is required",
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: "Invalid email",
            },
          }}
          render={({ field }) => (
            <TextField
              {...field}
              label="Email"
              error={!!errors.email}
              helperText={errors.email?.message}
              fullWidth
            />
          )}
        />
        
        <Controller
          name="password"
          control={control}
          rules={{
            required: "Password is required",
            minLength: { value: 8, message: "Min 8 characters" },
          }}
          render={({ field }) => (
            <TextField
              {...field}
              label="Password"
              type="password"
              error={!!errors.password}
              helperText={errors.password?.message}
              fullWidth
            />
          )}
        />
        
        <Button variant="contained" type="submit" fullWidth>
          Register
        </Button>
      </Stack>
    </form>
  )
}
```

## Data Grid

```bash
npm install @mui/x-data-grid
```

```tsx
import { DataGrid } from "@mui/x-data-grid"

const columns = [
  { field: "id", headerName: "ID", width: 70 },
  { field: "firstName", headerName: "First Name", width: 130 },
  { field: "lastName", headerName: "Last Name", width: 130 },
  { field: "email", headerName: "Email", width: 200 },
]

const rows = [
  { id: 1, firstName: "John", lastName: "Doe", email: "john@example.com" },
  { id: 2, firstName: "Jane", lastName: "Smith", email: "jane@example.com" },
]

export function DataTableDemo() {
  return (
    <div style={{ height: 400, width: "100%" }}>
      <DataGrid rows={rows} columns={columns} checkboxSelection />
    </div>
  )
}
```

## Best Practices

### 1. Use sx Prop for Styling

```tsx
// ✅ Good: Use sx for component-specific styles
<Box sx={{ padding: 2, backgroundColor: "primary.light" }}>
  Content
</Box>

// ❌ Avoid: Inline styles
<Box style={{ padding: "16px", backgroundColor: "lightblue" }}>
  Content
</Box>
```

### 2. Responsive Design

```tsx
// ✅ Good: Responsive values
<TextField
  sx={{
    width: { xs: "100%", sm: "80%", md: "50%" }
  }}
/>

// ❌ Avoid: Fixed widths
<TextField sx={{ width: "50%" }} />
```

### 3. Composition Over Nesting

```tsx
// ✅ Good: Compose from primitives
<Stack spacing={2}>
  <TextField label="Name" />
  <TextField label="Email" />
  <Button>Submit</Button>
</Stack>

// ❌ Avoid: Deep nesting
<Box><Stack><TextField /></Stack></Box>
```

### 4. Theme Consistency

```tsx
// ✅ Use theme colors
<Button sx={{ backgroundColor: "primary.main" }}>
  Action
</Button>

// ✅ Use spacing constants
<Stack spacing={2}>  {/* 2 = 16px */}
  <Button>Button 1</Button>
  <Button>Button 2</Button>
</Stack>
```

## MUI vs shadcn/ui Decision

**Choose MUI if:**
- Need Material Design specific
- Want npm package (not copy-paste)
- Need pre-built data grid
- Theme system important
- Team familiar with MUI

**Choose shadcn/ui if:**
- Want smaller bundle
- Prefer Tailwind CSS
- Want full code control
- Don't need Material Design
- Prefer copy-paste approach

**You can use BOTH:**
```tsx
// Use shadcn/ui for simple components
import { Button } from "@/components/ui/button"

// Use MUI for complex features
import { DataGrid } from "@mui/x-data-grid"
import { ThemeProvider } from "@mui/material/styles"
```

## Resources

- **MUI Docs:** https://mui.com
- **MUI Components:** https://mui.com/material-ui/api/
- **MUI Icons:** https://mui.com/material-ui/icons/
- **MUI X (Advanced):** https://mui.com/x/
- **Theming Guide:** https://mui.com/material-ui/customization/theming/

## Common Component Patterns

### Card with Icon

```tsx
import { Card, CardContent, Typography, Box } from "@mui/material"
import StorageIcon from "@mui/icons-material/Storage"

export function StorageCard() {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <StorageIcon sx={{ fontSize: 40, color: "primary.main" }} />
          <Box>
            <Typography color="textSecondary">Storage Used</Typography>
            <Typography variant="h5">450 GB / 1 TB</Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}
```

### Action Bar

```tsx
import { AppBar, Toolbar, Button, Stack, Typography } from "@mui/material"

export function ActionBar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          MyApp
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button color="inherit">Home</Button>
          <Button color="inherit">About</Button>
          <Button color="inherit">Contact</Button>
        </Stack>
      </Toolbar>
    </AppBar>
  )
}
```

