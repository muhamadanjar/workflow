# PostgreSQL Performance Optimization

Query optimization, indexing strategies, bottleneck identification.

## EXPLAIN ANALYZE

Understand query execution.

### Basic EXPLAIN

```sql
-- Show plan without executing
EXPLAIN
SELECT u.username, COUNT(p.id) as posts
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id;

-- Output: Sequential scan, cost, rows estimate
```

### EXPLAIN ANALYZE

```sql
-- Show plan AND actual execution stats
EXPLAIN ANALYZE
SELECT u.username, COUNT(p.id) as posts
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id;

-- Output: Shows estimated vs. actual rows, actual time
-- Use this to find inefficiencies
```

### Format Options

```sql
-- JSON format (machine readable)
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM users WHERE age > 25;

-- Verbose output
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM users WHERE age > 25;

-- Timing details
EXPLAIN (ANALYZE, TIMING)
SELECT * FROM users WHERE age > 25;

-- Buffer statistics
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users WHERE age > 25;
```

## Index Strategies

### Single Column Index

```sql
-- Index on frequently queried column
CREATE INDEX idx_users_email ON users(email);

-- Verify it's used
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';
-- Should show: Index Scan on idx_users_email

-- ✅ Good for:
-- WHERE email = 'value'
-- WHERE email LIKE 'pattern%'
-- ORDER BY email

-- ❌ Not helpful for:
-- WHERE email LIKE '%pattern'  (doesn't use index)
-- WHERE email IS NULL          (not indexed by default)
```

### Composite Index (Multi-column)

```sql
-- Index on (user_id, created_at)
CREATE INDEX idx_posts_user_date ON posts(user_id, created_at DESC);

-- Helpful for queries using both columns
EXPLAIN ANALYZE
SELECT * FROM posts
WHERE user_id = 1
ORDER BY created_at DESC;

-- ✅ Index supports:
-- WHERE user_id = 1         (first column)
-- WHERE user_id = 1 AND created_at > '2024-01-01'  (both columns)
-- ORDER BY created_at       (leverages DESC in index)

-- ❌ Index doesn't help:
-- WHERE created_at > '2024-01-01'  (created_at not first)
-- ORDER BY user_id, created_at     (wrong order)
```

### Partial Index

Index only matching rows.

```sql
-- Index only active users (most common case)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Smaller, faster
EXPLAIN ANALYZE
SELECT * FROM users WHERE status = 'active' AND email = 'test@example.com';
-- Uses partial index

-- Query for inactive doesn't use it
EXPLAIN ANALYZE
SELECT * FROM users WHERE status = 'inactive' AND email = 'test@example.com';
-- Sequential scan
```

### Expression Index

Index computed values.

```sql
-- Index LOWER(email) for case-insensitive queries
CREATE INDEX idx_lower_email ON users(LOWER(email));

-- Query using expression uses index
EXPLAIN ANALYZE
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';
-- Uses idx_lower_email

-- Without expression index
EXPLAIN ANALYZE
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';
-- Sequential scan (slow)
```

### Full-Text Search Index

```sql
-- Index for text search
CREATE INDEX idx_posts_search ON posts USING gin(to_tsvector('english', title || ' ' || content));

-- Fast text search
EXPLAIN ANALYZE
SELECT * FROM posts WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', 'database');

-- Relevant results ranked
SELECT id, title,
    ts_rank(to_tsvector('english', title || ' ' || content), 
           plainto_tsquery('english', 'database')) as relevance
FROM posts
WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', 'database')
ORDER BY relevance DESC;
```

### JSON/JSONB Index

```sql
-- Index JSONB fields
CREATE INDEX idx_users_metadata ON users USING gin(metadata);

-- Query using indexed field
EXPLAIN ANALYZE
SELECT * FROM users WHERE metadata @> '{"city": "NYC"}'::jsonb;
-- Uses gin index

-- Update JSON
UPDATE users SET metadata = jsonb_set(metadata, '{city}', '"NYC"')
WHERE id = 1;
```

## Query Optimization

### Use Appropriate JOIN Type

```sql
-- INNER JOIN (only matching)
SELECT u.username, p.title
FROM users u
INNER JOIN posts p ON u.id = p.user_id;

-- LEFT JOIN (all users, matching posts)
SELECT u.username, COUNT(p.id) as posts
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id;

-- Most efficient query form
EXPLAIN ANALYZE
SELECT u.username, COALESCE(COUNT(p.id), 0) as posts
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id;
```

### Filter Early

```sql
-- ❌ Slow: Filter after join
SELECT u.username, p.title
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
WHERE u.status = 'active';

-- ✅ Fast: Filter before join (smaller join size)
SELECT u.username, p.title
FROM (SELECT * FROM users WHERE status = 'active') u
LEFT JOIN posts p ON u.id = p.user_id;
-- Or simply:
SELECT u.username, p.title
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
WHERE u.status = 'active';
-- PostgreSQL optimizer knows to filter first
```

### Use Subqueries Wisely

```sql
-- ✅ CTE for readability and optimization
WITH active_users AS (
    SELECT id, username FROM users WHERE status = 'active'
)
SELECT au.username, COUNT(p.id) as posts
FROM active_users au
LEFT JOIN posts p ON au.id = p.user_id
GROUP BY au.id;

-- ✅ Materialized CTE (compute once)
WITH active_users AS MATERIALIZED (
    SELECT id, username FROM users WHERE status = 'active'
)
SELECT au.username, COUNT(p.id) as posts
FROM active_users au
LEFT JOIN posts p ON au.id = p.user_id
GROUP BY au.id;
```

### Batch Operations

```sql
-- ❌ Slow: Individual inserts
INSERT INTO users VALUES (1, 'john');
INSERT INTO users VALUES (2, 'jane');
INSERT INTO users VALUES (3, 'bob');

-- ✅ Fast: Batch insert
INSERT INTO users VALUES
    (1, 'john'),
    (2, 'jane'),
    (3, 'bob');

-- ✅ Very fast: Copy
COPY users (id, username) FROM STDIN;
1   john
2   jane
3   bob
\.
```

## Common Bottlenecks

### Missing Index

```sql
-- Slow query scanning entire table
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 1;
-- Seq Scan on orders (10M rows)

-- Add index
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Now fast
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 1;
-- Index Scan on idx_orders_user_id
```

### N+1 Query Problem

```sql
-- ❌ Slow: Loop with queries
users = SELECT * FROM users;
for user in users:
    posts = SELECT * FROM posts WHERE user_id = user.id;  -- N+1 queries

-- ✅ Fast: Single join
SELECT u.*, p.* FROM users u
LEFT JOIN posts p ON u.id = p.user_id;

-- Or: Use batch query
SELECT * FROM posts WHERE user_id IN (SELECT id FROM users);
```

### Large Result Set

```sql
-- ❌ Slow: Unnecessary columns
SELECT * FROM huge_table;

-- ✅ Fast: Select needed columns
SELECT id, name, email FROM huge_table;

-- ❌ Slow: All rows
SELECT * FROM orders;

-- ✅ Fast: Limit/offset (pagination)
SELECT * FROM orders LIMIT 20 OFFSET 0;
```

### Unindexed Sort

```sql
-- ❌ Slow: Sort on unindexed column
EXPLAIN ANALYZE
SELECT * FROM posts ORDER BY title;
-- Sort (slow)

-- ✅ Fast: Index on sort column
CREATE INDEX idx_posts_title ON posts(title);
EXPLAIN ANALYZE
SELECT * FROM posts ORDER BY title;
-- Index Scan

-- Or with join
EXPLAIN ANALYZE
SELECT u.username, p.title
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
ORDER BY u.username, p.created_at;

-- Index: idx_posts_user_date (user_id, created_at) helps
```

## Monitoring

### Check Index Usage

```sql
-- Find unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Drop unused (check carefully)
DROP INDEX idx_posts_old;
```

### Table Size

```sql
-- Size of each table
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Query Performance

```sql
-- Enable query logging
SET log_min_duration_statement = 1000;  -- Log queries > 1 second

-- View logs
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

## Optimization Checklist

- [ ] EXPLAIN ANALYZE reviewed for slow queries
- [ ] Indexes on WHERE columns
- [ ] Indexes on JOIN columns
- [ ] Indexes on ORDER BY columns
- [ ] No SELECT * (specify columns)
- [ ] Filter before JOIN (WHERE before INNER JOIN)
- [ ] Batch operations where possible
- [ ] Pagination used for large result sets
- [ ] CTEs for complex queries
- [ ] Materialized views for expensive aggregations
- [ ] Unused indexes removed
- [ ] Query logs monitored for slow queries

---

See **SECURITY.md** for SQL injection prevention and access control.

