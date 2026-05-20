# PostgreSQL Basics

DDL (Data Definition Language), DML (Data Manipulation Language), constraints, sequences.

## DDL - Creating Structures

### Database

```sql
-- Create
CREATE DATABASE myapp;

-- With options
CREATE DATABASE myapp
    OWNER postgres
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8'
    TEMPLATE template0;

-- Drop
DROP DATABASE IF EXISTS myapp;

-- List databases
\l  -- In psql
```

### Schema

```sql
-- Create schema (logical grouping)
CREATE SCHEMA app;
CREATE SCHEMA audit;
CREATE SCHEMA api;

-- Create table in schema
CREATE TABLE app.users (id SERIAL PRIMARY KEY);

-- Set default schema
SET search_path TO app, public;
SELECT * FROM users;  -- Found in app.users

-- Drop schema
DROP SCHEMA IF EXISTS app CASCADE;  -- CASCADE drops objects
```

### Table

```sql
-- Basic
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- With all features
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    stock INTEGER DEFAULT 0,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name),
    CONSTRAINT price_positive CHECK (price > 0)
);

-- Temporary table (dropped at session end)
CREATE TEMP TABLE temp_users AS
SELECT * FROM users;

-- Unlogged table (fast, not replicated)
CREATE UNLOGGED TABLE logs (
    id SERIAL,
    message TEXT,
    created_at TIMESTAMP
);
```

### Columns & Data Types

```sql
-- Numeric
INTEGER, BIGINT, SMALLINT
DECIMAL(precision, scale)  -- DECIMAL(10, 2) = 12345678.90
NUMERIC(10, 2)             -- Alias for DECIMAL
REAL, DOUBLE PRECISION     -- Floating point

-- Text
VARCHAR(n)                 -- Variable, max n chars
VARCHAR                    -- Unlimited
CHAR(n)                    -- Fixed length, padded
TEXT                       -- Unlimited (preferred)

-- Date/Time
DATE                       -- 2026-05-20
TIME                       -- 14:30:00
TIME WITH TIME ZONE        -- 14:30:00+02
TIMESTAMP                  -- 2026-05-20 14:30:00
TIMESTAMP WITH TIME ZONE   -- With timezone
INTERVAL                   -- Duration: 1 day 2 hours

-- Boolean
BOOLEAN                    -- true/false/NULL

-- Special
JSON, JSONB                -- JSON documents (JSONB indexed/searchable)
ARRAY                      -- Arrays: INTEGER[], TEXT[]
UUID                       -- Universally unique ID
BYTEA                      -- Binary data
ENUM                       -- Enumerated type
SERIAL, BIGSERIAL          -- Auto-increment integer
```

### Constraints

```sql
-- Primary Key (unique identifier)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);
-- Or:
CREATE TABLE users (
    id INTEGER,
    name VARCHAR(100),
    PRIMARY KEY (id)
);

-- Foreign Key (relationship to another table)
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255)
);
-- With cascade
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255)
);

-- Unique constraint
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);

-- NOT NULL constraint
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL
);

-- Check constraint (validate condition)
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    price DECIMAL(10, 2) CHECK (price > 0),
    stock INTEGER CHECK (stock >= 0)
);

-- Multiple columns (composite key)
CREATE TABLE enrollments (
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    PRIMARY KEY (student_id, course_id)
);

-- Default value
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);
```

### Index

```sql
-- Single column
CREATE INDEX idx_users_email ON users(email);

-- Multiple columns (composite)
CREATE INDEX idx_posts_user_date ON posts(user_id, created_at DESC);

-- Unique index (enforces uniqueness)
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Partial index (indexed rows matching condition)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Full-text search index
CREATE INDEX idx_posts_search ON posts USING gin(to_tsvector('english', title || ' ' || content));

-- Drop index
DROP INDEX idx_users_email;

-- List indexes
\di table_name
```

### View

```sql
-- Simple view (virtual table)
CREATE VIEW user_stats AS
SELECT 
    user_id,
    COUNT(*) as post_count,
    MAX(created_at) as last_post
FROM posts
GROUP BY user_id;

-- Query view
SELECT * FROM user_stats;

-- Materialized view (stores results, needs refresh)
CREATE MATERIALIZED VIEW user_stats_cached AS
SELECT 
    user_id,
    COUNT(*) as post_count,
    MAX(created_at) as last_post
FROM posts
GROUP BY user_id;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW user_stats_cached;

-- Drop view
DROP VIEW user_stats;
DROP MATERIALIZED VIEW user_stats_cached;
```

### Sequence (Auto-increment)

```sql
-- Explicit sequence
CREATE SEQUENCE users_id_seq START 1 INCREMENT 1;

-- Use in table
CREATE TABLE users (
    id INTEGER DEFAULT nextval('users_id_seq') PRIMARY KEY,
    name VARCHAR(100)
);

-- Or SERIAL (shorthand)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,  -- SERIAL = shorthand
    name VARCHAR(100)
);

-- Get next value
SELECT nextval('users_id_seq');

-- Set sequence value
SELECT setval('users_id_seq', 1000);

-- Drop sequence
DROP SEQUENCE users_id_seq;
```

## DML - Manipulating Data

### INSERT

```sql
-- Single row
INSERT INTO users (username, email) VALUES ('john', 'john@example.com');

-- Multiple rows
INSERT INTO users (username, email) VALUES
    ('jane', 'jane@example.com'),
    ('bob', 'bob@example.com');

-- From SELECT
INSERT INTO users_backup
SELECT * FROM users WHERE created_at < NOW() - INTERVAL '1 year';

-- With RETURNING (see inserted data)
INSERT INTO users (username, email) 
VALUES ('alice', 'alice@example.com')
RETURNING id, username, created_at;

-- Ignore duplicates
INSERT INTO users (username, email) VALUES ('john', 'john@example.com')
ON CONFLICT (username) DO NOTHING;

-- Update on duplicate
INSERT INTO users (username, email) VALUES ('john', 'john2@example.com')
ON CONFLICT (username) DO UPDATE SET email = EXCLUDED.email;
```

### UPDATE

```sql
-- Basic
UPDATE users SET email = 'newemail@example.com' WHERE id = 1;

-- Multiple columns
UPDATE users SET 
    email = 'new@example.com',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 1;

-- Computed update
UPDATE products SET price = price * 1.1 WHERE category = 'sale';

-- From another table
UPDATE users SET status = 'premium'
FROM subscriptions
WHERE users.id = subscriptions.user_id AND subscriptions.active = true;

-- With RETURNING
UPDATE users SET email = 'new@example.com' WHERE id = 1
RETURNING id, email, updated_at;

-- Bulk update
UPDATE users SET status = 'inactive' WHERE last_login < NOW() - INTERVAL '1 year';
```

### DELETE

```sql
-- Delete rows
DELETE FROM users WHERE id = 1;

-- Delete multiple
DELETE FROM users WHERE status = 'inactive' AND created_at < NOW() - INTERVAL '1 year';

-- Delete all
DELETE FROM users;

-- With RETURNING
DELETE FROM users WHERE id = 1
RETURNING id, username;

-- Delete cascade (if FK configured)
DELETE FROM categories WHERE id = 1;  -- Auto-deletes related products
```

### SELECT

```sql
-- All columns
SELECT * FROM users;

-- Specific columns
SELECT id, username, email FROM users;

-- With WHERE
SELECT * FROM users WHERE age > 25 AND status = 'active';

-- ORDER BY
SELECT * FROM users ORDER BY created_at DESC;

-- LIMIT & OFFSET
SELECT * FROM users LIMIT 10 OFFSET 20;  -- Page 3 (0-20 skipped)

-- DISTINCT (unique values)
SELECT DISTINCT status FROM users;

-- Aggregation
SELECT COUNT(*), AVG(age), MAX(salary) FROM employees;

-- GROUP BY
SELECT department_id, COUNT(*), AVG(salary) 
FROM employees 
GROUP BY department_id;

-- HAVING (filter grouped results)
SELECT department_id, COUNT(*) as count, AVG(salary) as avg_sal
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5 AND AVG(salary) > 50000;

-- CASE (conditional)
SELECT 
    id,
    username,
    CASE 
        WHEN age < 18 THEN 'Minor'
        WHEN age < 65 THEN 'Adult'
        ELSE 'Senior'
    END as age_group
FROM users;
```

## Common Patterns

### Upsert (Insert or Update)

```sql
-- If exists, update; otherwise insert
INSERT INTO users (username, email) VALUES ('john', 'john@example.com')
ON CONFLICT (username) DO UPDATE SET
    email = EXCLUDED.email,
    updated_at = CURRENT_TIMESTAMP;
```

### Soft Delete (Mark as deleted, don't remove)

```sql
-- Add deleted_at column
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;

-- Soft delete
UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = 1;

-- Query only active
SELECT * FROM users WHERE deleted_at IS NULL;

-- Hard delete (permanent)
DELETE FROM users WHERE deleted_at IS NOT NULL AND deleted_at < NOW() - INTERVAL '90 days';
```

### Audit Trail

```sql
-- Add timestamps
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Update updated_at on every change
-- (Better with trigger, see ADVANCED.md)
UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

### Bulk Operations

```sql
-- Efficient bulk insert (from file)
COPY users (username, email) FROM '/tmp/users.csv' WITH CSV HEADER;

-- Export to file
COPY users TO '/tmp/users_backup.csv' WITH CSV HEADER;

-- Bulk update
UPDATE users SET status = 'premium' 
WHERE id IN (SELECT user_id FROM subscriptions WHERE active = true);
```

## Transactions

```sql
-- Explicit transaction
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Rollback on error
BEGIN;
    UPDATE users SET email = 'test@example.com' WHERE id = 1;
    -- Error occurs
ROLLBACK;  -- Undo all changes

-- Savepoint (partial rollback)
BEGIN;
    UPDATE users SET status = 'active' WHERE id = 1;
    SAVEPOINT sp1;
    
    UPDATE users SET email = 'invalid' WHERE id = 2;  -- Error
    ROLLBACK TO sp1;  -- Undo email update, keep status update
    
    UPDATE users SET email = 'valid@example.com' WHERE id = 2;
COMMIT;

-- ACID properties
-- Atomicity: All or nothing
-- Consistency: Valid state always
-- Isolation: Concurrent transactions don't interfere
-- Durability: Committed data persists
```

## Data Types - Examples

```sql
CREATE TABLE examples (
    -- Numeric
    id SERIAL PRIMARY KEY,
    count INTEGER,
    salary DECIMAL(10, 2),
    rate REAL,
    
    -- Text
    name VARCHAR(100),
    description TEXT,
    
    -- Date/Time
    birth_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Boolean
    is_active BOOLEAN DEFAULT true,
    
    -- Arrays
    tags TEXT[],
    scores INTEGER[],
    
    -- JSON
    metadata JSONB,
    
    -- Special
    profile_id UUID,
    file_data BYTEA
);

-- Insert examples
INSERT INTO examples (
    name, 
    salary, 
    tags, 
    metadata
) VALUES (
    'John',
    50000.50,
    ARRAY['python', 'postgresql'],
    '{"department": "engineering", "level": 3}'::jsonb
);

-- Query
SELECT 
    id,
    name,
    salary,
    tags[1] as first_tag,
    metadata->>'department' as department
FROM examples;
```

## Checklist

- [ ] Database created and connected
- [ ] Schema structure planned (logical grouping)
- [ ] Tables with appropriate data types
- [ ] Primary keys on all tables
- [ ] Foreign keys for relationships
- [ ] NOT NULL constraints where needed
- [ ] UNIQUE constraints on identifiers
- [ ] CHECK constraints for valid ranges
- [ ] Indexes on frequently queried columns
- [ ] Transactions for multi-step operations

---

See **INTERMEDIATE.md** for joins, subqueries, window functions.

