# PostgreSQL Database Design

Complete guide: basic DDL to professional patterns (stored procedures, triggers, optimization).

## Overview

PostgreSQL: enterprise-grade relational database. ACID compliant, extensible, mature.

**Key Features:**
- Full ACID transactions
- Stored procedures (PL/pgSQL, Python, JavaScript)
- Triggers and rules
- Window functions, CTEs
- Full-text search, JSON, arrays
- Row-level security
- Partitioning, replication

## Quick Start

```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Linux (Ubuntu): sudo apt install postgresql
# Windows: https://www.postgresql.org/download/windows/

# Start service
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Connect to database
psql -U postgres -d template1

# Or via docker
docker run -d \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:latest
```

## Basic Concepts

### Database > Schema > Table

```sql
-- Create database
CREATE DATABASE myapp;

-- Connect
\c myapp

-- Create schema (logical grouping)
CREATE SCHEMA app;
CREATE SCHEMA audit;

-- Create table in schema
CREATE TABLE app.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query with schema
SELECT * FROM app.users;
```

### Data Types

```sql
-- Numeric
SMALLINT, INTEGER, BIGINT  -- -32K to 2B to 9.2Q
DECIMAL(10,2), NUMERIC     -- Fixed precision
REAL, DOUBLE PRECISION     -- Floating point

-- Text
VARCHAR(n), CHAR(n)        -- Variable/fixed length
TEXT                       -- Unlimited

-- Date/Time
DATE, TIME, TIMESTAMP      -- Date, time, datetime
INTERVAL                   -- Duration

-- Boolean
BOOLEAN                    -- true/false

-- Special
JSON, JSONB                -- JSON documents
ARRAY                      -- Arrays
UUID                       -- Universally unique
BYTEA                      -- Binary data
```

## Common Patterns

### Entity Relationships

```sql
-- One-to-Many
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department_id INTEGER REFERENCES departments(id)
);

-- Many-to-Many
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE enrollments (
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    PRIMARY KEY (student_id, course_id)
);

-- Self-referential (hierarchical)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    parent_id INTEGER REFERENCES categories(id)
);
```

### Audit Trail

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(10),  -- INSERT, UPDATE, DELETE
    record_id INTEGER,
    old_data JSONB,
    new_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);
```

## Key Files

- **BASICS.md** — DDL, DML, constraints, sequences
- **INTERMEDIATE.md** — Joins, subqueries, CTEs, window functions, indexes
- **ADVANCED.md** — Stored procedures, triggers, transactions, optimization
- **PATTERNS.md** — Design patterns, normalization, anti-patterns
- **PERFORMANCE.md** — Query optimization, EXPLAIN ANALYZE, indexing strategies
- **SECURITY.md** — SQL injection prevention, RLS, access control
- **EXAMPLES.md** — Real-world schemas (e-commerce, social, blog)

## Architecture Layers

```
Application
    ↓
Queries (SELECT, INSERT, UPDATE, DELETE)
    ↓
Views (virtual tables, simplified access)
    ↓
Stored Procedures (business logic)
    ↓
Triggers (automatic actions)
    ↓
Tables (raw data storage)
    ↓
Indexes (query acceleration)
    ↓
Physical Storage (disk)
```

## Common Tasks

### Create Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER CHECK (age >= 18),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Insert Data
```sql
INSERT INTO users (name, email, age) 
VALUES ('John', 'john@example.com', 30);

INSERT INTO users (name, email, age) VALUES
    ('Jane', 'jane@example.com', 28),
    ('Bob', 'bob@example.com', 35);
```

### Query Data
```sql
SELECT * FROM users WHERE age > 25 ORDER BY name;
SELECT COUNT(*), AVG(age) FROM users;
SELECT name, email FROM users WHERE name LIKE 'J%';
```

### Update Data
```sql
UPDATE users SET age = 31 WHERE name = 'John';
UPDATE users SET age = age + 1 WHERE age > 50;
```

### Delete Data
```sql
DELETE FROM users WHERE id = 1;
DELETE FROM users WHERE created_at < NOW() - INTERVAL '1 year';
```

## Design Principles

✅ **Normalization** — Eliminate redundancy, maintain integrity
✅ **Constraints** — PK, FK, UNIQUE, NOT NULL, CHECK
✅ **Relationships** — Clear, enforced via foreign keys
✅ **Indexes** — Strategic placement for performance
✅ **Partitioning** — Large tables split by range/hash
✅ **Archiving** — Move old data to separate tables
✅ **Transactions** — ACID compliance for data safety

❌ **Avoid:**
- Storing computed values (use views)
- Redundant data (normalize instead)
- Over-indexing (maintenance cost)
- SELECT * (specify columns)
- Missing constraints (rely on application)

## Testing Queries

```bash
# Connect and test
psql -U postgres -d myapp

# List tables
\dt

# Describe table
\d table_name

# Run query
SELECT * FROM users;

# Run script
psql -U postgres -d myapp -f schema.sql

# Benchmark query
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 25;

# Exit
\q
```

## Tools

**psql** — Command-line client (built-in)
**pgAdmin** — Web UI (https://www.pgadmin.org)
**DBeaver** — Desktop client (https://dbeaver.io)
**Adminer** — Single PHP file UI
**DataGrip** — JetBrains IDE

## Resources

- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [PostgreSQL 15 Manual](https://www.postgresql.org/docs/15/index.html)
- [PL/pgSQL Docs](https://www.postgresql.org/docs/current/plpgsql.html)
- [Triggers Guide](https://www.postgresql.org/docs/current/sql-createtrigger.html)

---

**Start with BASICS.md** for DDL/DML fundamentals.

