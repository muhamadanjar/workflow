# TanStack React Table v8 — Basic to Professional

## Installation

```bash
npm install @tanstack/react-table
```

---

## Level 1: Basic Table

### Minimal setup

```tsx
// components/table/BasicTable.tsx
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

const columnHelper = createColumnHelper<User>();

const columns = [
  columnHelper.accessor("name", {
    header: "Name",
    cell: (info) => info.getValue(),
  }),
  columnHelper.accessor("email", {
    header: "Email",
  }),
  columnHelper.accessor("role", {
    header: "Role",
  }),
];

export function BasicTable({ data }: { data: User[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => (
              <th key={header.id}>
                {flexRender(header.column.columnDef.header, header.getContext())}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => (
          <tr key={row.id}>
            {row.getVisibleCells().map((cell) => (
              <td key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

## Level 2: Sorting + Filtering + Pagination

### Client-side features

```tsx
// components/table/DataTable.tsx
import { useState } from "react";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type SortingState,
  type ColumnFiltersState,
} from "@tanstack/react-table";

const columnHelper = createColumnHelper<User>();

const columns = [
  columnHelper.accessor("name", {
    header: ({ column }) => (
      <button onClick={() => column.toggleSorting()}>
        Name {column.getIsSorted() === "asc" ? "↑" : column.getIsSorted() === "desc" ? "↓" : "↕"}
      </button>
    ),
    filterFn: "includesString",
  }),
  columnHelper.accessor("email", { header: "Email" }),
  columnHelper.accessor("role", {
    header: "Role",
    filterFn: "equalsString",
  }),
];

export function DataTable({ data }: { data: User[] }) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, globalFilter },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 10 } },
  });

  return (
    <div className="space-y-4">
      {/* Global Search */}
      <input
        value={globalFilter}
        onChange={(e) => setGlobalFilter(e.target.value)}
        placeholder="Search all columns..."
        className="border px-3 py-2 rounded"
      />

      {/* Table */}
      <table className="w-full border-collapse">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id} className="border-b">
              {headerGroup.headers.map((header) => (
                <th key={header.id} className="text-left p-2">
                  {flexRender(header.column.columnDef.header, header.getContext())}
                  {/* Per-column filter */}
                  {header.column.getCanFilter() && (
                    <input
                      value={(header.column.getFilterValue() as string) ?? ""}
                      onChange={(e) => header.column.setFilterValue(e.target.value)}
                      placeholder={`Filter ${header.column.id}...`}
                      className="block mt-1 border px-2 py-1 text-sm rounded"
                    />
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="border-b hover:bg-gray-50">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="p-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      <div className="flex items-center gap-2">
        <button onClick={() => table.setPageIndex(0)} disabled={!table.getCanPreviousPage()}>«</button>
        <button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>‹</button>
        <span>
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
        </span>
        <button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>›</button>
        <button onClick={() => table.setPageIndex(table.getPageCount() - 1)} disabled={!table.getCanNextPage()}>»</button>
        <select
          value={table.getState().pagination.pageSize}
          onChange={(e) => table.setPageSize(Number(e.target.value))}
        >
          {[10, 20, 50, 100].map((size) => (
            <option key={size} value={size}>Show {size}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
```

---

## Level 3: Row Selection + Custom Cell Rendering

```tsx
import { type RowSelectionState } from "@tanstack/react-table";

const columns = [
  // Checkbox column
  columnHelper.display({
    id: "select",
    header: ({ table }) => (
      <input
        type="checkbox"
        checked={table.getIsAllPageRowsSelected()}
        indeterminate={table.getIsSomePageRowsSelected()}
        onChange={table.getToggleAllPageRowsSelectedHandler()}
      />
    ),
    cell: ({ row }) => (
      <input
        type="checkbox"
        checked={row.getIsSelected()}
        disabled={!row.getCanSelect()}
        onChange={row.getToggleSelectedHandler()}
      />
    ),
  }),
  columnHelper.accessor("name", {
    header: "Name",
    cell: ({ row, getValue }) => (
      <div className="flex items-center gap-2">
        <img
          src={row.original.avatar}
          alt={getValue()}
          className="w-8 h-8 rounded-full"
        />
        <span className="font-medium">{getValue()}</span>
      </div>
    ),
  }),
  columnHelper.accessor("status", {
    header: "Status",
    cell: ({ getValue }) => {
      const status = getValue();
      return (
        <span className={`px-2 py-1 rounded-full text-xs ${
          status === "active" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
        }`}>
          {status}
        </span>
      );
    },
  }),
  // Actions column
  columnHelper.display({
    id: "actions",
    header: "Actions",
    cell: ({ row }) => (
      <div className="flex gap-2">
        <button onClick={() => handleEdit(row.original)}>Edit</button>
        <button onClick={() => handleDelete(row.original.id)}>Delete</button>
      </div>
    ),
  }),
];

// Usage
const [rowSelection, setRowSelection] = useState<RowSelectionState>({});

const table = useReactTable({
  data,
  columns,
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  enableRowSelection: true,
  getCoreRowModel: getCoreRowModel(),
});

// Get selected rows data
const selectedRows = table.getSelectedRowModel().rows.map((r) => r.original);
```

---

## Level 4: Column Visibility + Reordering + Pinning

```tsx
import {
  type ColumnOrderState,
  type VisibilityState,
} from "@tanstack/react-table";

export function AdvancedTable({ data }: { data: User[] }) {
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [columnOrder, setColumnOrder] = useState<ColumnOrderState>([]);

  const table = useReactTable({
    data,
    columns,
    state: { columnVisibility, columnOrder },
    onColumnVisibilityChange: setColumnVisibility,
    onColumnOrderChange: setColumnOrder,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div>
      {/* Column visibility toggles */}
      <div className="flex gap-2 mb-4">
        {table.getAllLeafColumns().map((column) => (
          <label key={column.id} className="flex items-center gap-1">
            <input
              type="checkbox"
              checked={column.getIsVisible()}
              onChange={column.getToggleVisibilityHandler()}
            />
            {column.id}
          </label>
        ))}
      </div>

      {/* Column pinning */}
      <button onClick={() => table.getColumn("name")?.pin("left")}>
        Pin Name Left
      </button>

      {/* Table render */}
      <table>...</table>
    </div>
  );
}
```

---

## Level 5: Server-Side Table (with React Query)

### Full server-side: sorting, filtering, pagination

```tsx
// components/table/ServerTable.tsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  useReactTable,
  getCoreRowModel,
  type SortingState,
  type PaginationState,
  type ColumnFiltersState,
} from "@tanstack/react-table";

interface TableParams {
  page: number;
  pageSize: number;
  sorting: SortingState;
  filters: ColumnFiltersState;
  globalFilter: string;
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

async function fetchUsers(params: TableParams): Promise<PaginatedResponse<User>> {
  const searchParams = new URLSearchParams({
    page: String(params.page),
    pageSize: String(params.pageSize),
    globalFilter: params.globalFilter,
  });

  params.sorting.forEach((sort) => {
    searchParams.append("sort", `${sort.id}:${sort.desc ? "desc" : "asc"}`);
  });

  params.filters.forEach((filter) => {
    searchParams.append(`filter_${filter.id}`, String(filter.value));
  });

  const res = await fetch(`/api/users?${searchParams}`);
  if (!res.ok) throw new Error("Failed to fetch users");
  return res.json();
}

export function ServerTable() {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [{ pageIndex, pageSize }, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const params: TableParams = {
    page: pageIndex,
    pageSize,
    sorting,
    filters: columnFilters,
    globalFilter,
  };

  const { data, isLoading, isError } = useQuery({
    queryKey: ["users", params],
    queryFn: () => fetchUsers(params),
    placeholderData: (prev) => prev, // keep previous data while loading
  });

  const table = useReactTable({
    data: data?.data ?? [],
    columns,
    rowCount: data?.total ?? 0,
    state: { sorting, columnFilters, globalFilter, pagination: { pageIndex, pageSize } },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    onPaginationChange: setPagination,
    manualSorting: true,
    manualFiltering: true,
    manualPagination: true,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error loading data</div>;

  return (
    <div>
      {/* Table render same as before */}
    </div>
  );
}
```

---

## Level 6: Virtualized Table (Large Datasets)

### 10k+ rows with `@tanstack/react-virtual`

```bash
npm install @tanstack/react-virtual
```

```tsx
// components/table/VirtualTable.tsx
import { useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useReactTable, getCoreRowModel } from "@tanstack/react-table";

export function VirtualTable({ data }: { data: User[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const { rows } = table.getRowModel();
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48, // row height estimate
    overscan: 10,
  });

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <table className="w-full">
        <thead className="sticky top-0 bg-white z-10">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id} className="p-2 text-left">
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody
          style={{ height: `${virtualizer.getTotalSize()}px`, position: "relative" }}
        >
          {virtualizer.getVirtualItems().map((virtualRow) => {
            const row = rows[virtualRow.index];
            return (
              <tr
                key={row.id}
                style={{
                  position: "absolute",
                  top: 0,
                  transform: `translateY(${virtualRow.start}px)`,
                  width: "100%",
                }}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="p-2">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
```

---

## Level 7: Reusable Generic DataTable Component

### Production-grade abstraction

```tsx
// components/table/DataTable.tsx
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
  type VisibilityState,
  type RowSelectionState,
} from "@tanstack/react-table";
import { useState } from "react";

interface DataTableProps<TData> {
  data: TData[];
  columns: ColumnDef<TData, unknown>[];
  enableSelection?: boolean;
  enableGlobalFilter?: boolean;
  pageSize?: number;
  onSelectionChange?: (rows: TData[]) => void;
  isLoading?: boolean;
  emptyState?: React.ReactNode;
}

export function DataTable<TData>({
  data,
  columns,
  enableSelection = false,
  enableGlobalFilter = true,
  pageSize = 10,
  onSelectionChange,
  isLoading,
  emptyState,
}: DataTableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
  const [globalFilter, setGlobalFilter] = useState("");

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, columnVisibility, rowSelection, globalFilter },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: (updater) => {
      setRowSelection(updater);
      if (onSelectionChange) {
        const next = typeof updater === "function" ? updater(rowSelection) : updater;
        const selected = Object.keys(next)
          .filter((k) => next[k])
          .map((k) => data[Number(k)]);
        onSelectionChange(selected);
      }
    },
    onGlobalFilterChange: setGlobalFilter,
    enableRowSelection: enableSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize } },
  });

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: pageSize }).map((_, i) => (
          <div key={i} className="h-12 bg-gray-100 animate-pulse rounded" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {enableGlobalFilter && (
        <input
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          placeholder="Search..."
          className="border px-3 py-2 rounded w-full"
        />
      )}

      <div className="rounded border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => (
                  <th
                    key={header.id}
                    className="p-3 text-left text-sm font-medium text-gray-500 cursor-pointer select-none"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    {{ asc: " ↑", desc: " ↓" }[header.column.getIsSorted() as string] ?? ""}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y">
            {table.getRowModel().rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="p-8 text-center text-gray-500">
                  {emptyState ?? "No data found"}
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="p-3 text-sm">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination controls */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-500">
          {enableSelection && `${Object.keys(rowSelection).length} selected · `}
          {table.getFilteredRowModel().rows.length} rows
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="px-3 py-1 border rounded disabled:opacity-40"
          >
            Prev
          </button>
          <span className="px-3 py-1 text-sm">
            {table.getState().pagination.pageIndex + 1} / {table.getPageCount()}
          </span>
          <button
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="px-3 py-1 border rounded disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Usage

```tsx
// Define columns outside component to avoid re-renders
const userColumns: ColumnDef<User>[] = [
  { accessorKey: "name", header: "Name" },
  { accessorKey: "email", header: "Email" },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ getValue }) => <StatusBadge status={getValue() as string} />,
  },
  {
    id: "actions",
    cell: ({ row }) => <UserActions user={row.original} />,
  },
];

function UsersPage() {
  return (
    <DataTable
      data={users}
      columns={userColumns}
      enableSelection
      onSelectionChange={(selected) => console.log(selected)}
    />
  );
}
```

---

## Column Definition Patterns

```tsx
// Accessor column (maps to data key)
columnHelper.accessor("email", {
  header: "Email",
  enableSorting: true,
  enableColumnFilter: true,
  size: 200,       // width hint
  minSize: 100,
  maxSize: 400,
});

// Display column (no data access)
columnHelper.display({
  id: "actions",
  header: () => null,
  cell: ({ row }) => <Actions row={row.original} />,
  enableSorting: false,
  enableHiding: false,
});

// Grouped columns
columnHelper.group({
  id: "contact",
  header: "Contact Info",
  columns: [
    columnHelper.accessor("email", { header: "Email" }),
    columnHelper.accessor("phone", { header: "Phone" }),
  ],
});
```

---

## Custom Filter Functions

```tsx
import { type FilterFn } from "@tanstack/react-table";

// Custom date range filter
const dateRangeFilter: FilterFn<User> = (row, columnId, value) => {
  const date = new Date(row.getValue(columnId));
  const [start, end] = value as [Date, Date];
  return date >= start && date <= end;
};

// Register on column
columnHelper.accessor("createdAt", {
  filterFn: dateRangeFilter,
});

// Custom fuzzy search
import { rankItem } from "@tanstack/match-sorter-utils";

const fuzzyFilter: FilterFn<unknown> = (row, columnId, value, addMeta) => {
  const itemRank = rankItem(row.getValue(columnId), value);
  addMeta({ itemRank });
  return itemRank.passed;
};

const table = useReactTable({
  globalFilterFn: fuzzyFilter,
  // ...
});
```

---

## Best Practices

```tsx
// ✅ Define columns outside component (stable reference)
const columns = useMemo(() => [...], []);

// ✅ Use columnHelper for type safety
const columnHelper = createColumnHelper<MyType>();

// ✅ manualPagination + manualSorting for server-side
const table = useReactTable({
  manualPagination: true,
  manualSorting: true,
  rowCount: serverTotal, // required for page count
});

// ✅ placeholderData for smooth UX during page change
const { data } = useQuery({
  queryKey: ["table", params],
  placeholderData: (prev) => prev,
});

// ❌ Avoid redefining columns inside render
// BAD:
function Table() {
  const columns = [...]; // new ref each render
}
```

---

## shadcn/ui Integration

```tsx
// components/ui/data-table.tsx — shadcn-style
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// Same DataTable logic, swap HTML elements with shadcn components
// Replace <table> → <Table>, <thead> → <TableHeader>, etc.
```

---

## MUI Integration

```tsx
import { TableContainer, Table, TableHead, TableRow, TableCell, TableBody, Paper } from "@mui/material";

// Same TanStack Table logic, swap elements with MUI components
<TableContainer component={Paper}>
  <Table>
    <TableHead>
      {table.getHeaderGroups().map((hg) => (
        <TableRow key={hg.id}>
          {hg.headers.map((header) => (
            <TableCell key={header.id}>
              {flexRender(header.column.columnDef.header, header.getContext())}
            </TableCell>
          ))}
        </TableRow>
      ))}
    </TableHead>
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
</TableContainer>
```
