# PostgreSQL Design Patterns

Database design patterns, anti-patterns, normalization, best practices.

## Normalization

Remove redundancy, maintain integrity.

### 1NF (First Normal Form)

Atomic values (no arrays/lists in columns).

```sql
-- ❌ Bad: Array in column
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    ratings INTEGER[]  -- [5, 4, 3, 5]
);

-- ✅ Good: Separate table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    rating INTEGER
);
```

### 2NF (Second Normal Form)

Non-key columns depend on entire primary key (not part of it).

```sql
-- ❌ Bad: Department name in employee table
CREATE TABLE employees (
    id SERIAL,
    name VARCHAR(100),
    department_id INTEGER,
    department_name VARCHAR(100),  -- Depends on dept_id, not employee
    PRIMARY KEY (id)
);

-- ✅ Good: Separate tables
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department_id INTEGER REFERENCES departments(id)
);
```

### 3NF (Third Normal Form)

Non-key columns don't depend on other non-key columns.

```sql
-- ❌ Bad: Transitive dependency
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    user_name VARCHAR(100),  -- Depends on user_id
    user_email VARCHAR(255)   -- Depends on user_id, not orders
);

-- ✅ Good: User in separate table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id)
);
```

## Relationship Patterns

### One-to-Many

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100)
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255)
);

-- User can have many posts
SELECT u.username, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id;
```

### Many-to-Many

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100)
);

-- Junction table
CREATE TABLE enrollments (
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    grade CHAR(1),
    PRIMARY KEY (student_id, course_id)
);

-- Student can enroll in many courses
SELECT s.name, COUNT(e.course_id) as course_count
FROM students s
LEFT JOIN enrollments e ON s.id = e.student_id
GROUP BY s.id;
```

### Self-Referential (Hierarchical)

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
);

-- Find direct children
SELECT * FROM categories WHERE parent_id = 1;

-- Find all descendants (recursive CTE)
WITH RECURSIVE descendants AS (
    SELECT id, name, 0 as level FROM categories WHERE parent_id = 1
    UNION ALL
    SELECT c.id, c.name, d.level + 1
    FROM categories c
    INNER JOIN descendants d ON c.parent_id = d.id
)
SELECT * FROM descendants;
```

## Temporal Patterns

### Soft Delete

Mark deleted, don't remove.

```sql
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;

-- Soft delete
UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = 1;

-- Query active only
SELECT * FROM users WHERE deleted_at IS NULL;

-- Recover
UPDATE users SET deleted_at = NULL WHERE id = 1;

-- Hard delete (after retention period)
DELETE FROM users WHERE deleted_at IS NOT NULL AND deleted_at < NOW() - INTERVAL '90 days';
```

### Audit Trail (Full History)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    username VARCHAR(100),
    email VARCHAR(255),
    operation VARCHAR(10),  -- INSERT, UPDATE, DELETE
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100)
);

-- Insert via trigger
CREATE FUNCTION audit_users()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO users_history (user_id, username, email, operation, changed_by)
    VALUES (
        COALESCE(NEW.id, OLD.id),
        COALESCE(NEW.username, OLD.username),
        COALESCE(NEW.email, OLD.email),
        TG_OP,
        CURRENT_USER
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_audit
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_users();

-- View history
SELECT * FROM users_history WHERE user_id = 1 ORDER BY changed_at;
```

### Slowly Changing Dimension (SCD Type 2)

Track historical versions.

```sql
CREATE TABLE products (
    product_id SERIAL,
    sku VARCHAR(50),
    name VARCHAR(255),
    price DECIMAL(10, 2),
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN DEFAULT true,
    PRIMARY KEY (product_id, valid_from)
);

-- When price changes, close old version and open new
UPDATE products SET valid_to = CURRENT_DATE - 1, is_current = false
WHERE sku = 'ABC123' AND is_current = true;

INSERT INTO products (sku, name, price, valid_from, is_current)
VALUES ('ABC123', 'Product', 99.99, CURRENT_DATE, true);

-- Get current version
SELECT * FROM products WHERE sku = 'ABC123' AND is_current = true;

-- Get historical price at date
SELECT price FROM products 
WHERE sku = 'ABC123' AND '2023-06-15'::DATE BETWEEN valid_from AND valid_to;
```

## Polymorphic Patterns

### Polymorphic Association (Multiple types reference same entity)

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    commentable_type VARCHAR(50),  -- 'post', 'photo', 'video'
    commentable_id INTEGER,
    user_id INTEGER REFERENCES users(id),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comment on post
INSERT INTO comments (commentable_type, commentable_id, user_id, content)
VALUES ('post', 1, 1, 'Great post!');

-- Comment on photo
INSERT INTO comments (commentable_type, commentable_id, user_id, content)
VALUES ('photo', 5, 1, 'Nice photo!');

-- Query comments for post
SELECT * FROM comments WHERE commentable_type = 'post' AND commentable_id = 1;

-- ⚠️ No FK constraint (data integrity risk)
-- Better: Use separate junction tables (see Many-to-Many pattern)
```

## Statistical Patterns

### Pre-computed Statistics

Cache aggregations.

```sql
CREATE TABLE user_stats (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE PRIMARY KEY,
    post_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    follower_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Update stats when post added
CREATE FUNCTION update_user_stats_on_post()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_stats SET
        post_count = post_count + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER posts_update_stats
AFTER INSERT ON posts
FOR EACH ROW EXECUTE FUNCTION update_user_stats_on_post();

-- Fast query (no expensive aggregation)
SELECT username, post_count, comment_count
FROM users u
JOIN user_stats s ON u.id = s.user_id;
```

## JSON Patterns

### EAV (Entity-Attribute-Value) as JSON

Store flexible attributes.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb  -- Flexible fields
);

INSERT INTO users (username, metadata) VALUES (
    'john',
    '{
        "age": 30,
        "city": "NYC",
        "preferences": {"theme": "dark", "language": "en"},
        "tags": ["vip", "verified"]
    }'::jsonb
);

-- Query
SELECT username, metadata->>'age' as age FROM users;
SELECT username, metadata->'preferences'->>'theme' as theme FROM users;

-- Update nested field
UPDATE users SET metadata = jsonb_set(metadata, '{preferences, theme}', '"light"')
WHERE id = 1;
```

## Anti-Patterns

### N+1 Query Problem

❌ Bad: Query in loop
```python
users = db.query("SELECT * FROM users")
for user in users:
    posts = db.query("SELECT * FROM posts WHERE user_id = %s", user.id)  # N queries
```

✅ Good: Single JOIN
```python
result = db.query("""
    SELECT u.*, p.* FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
""")
```

### Missing Indexes

❌ Bad: Sequential scan
```sql
SELECT * FROM orders WHERE user_id = 1 AND created_at > '2024-01-01';
-- Scans all 10M rows
```

✅ Good: Index on WHERE columns
```sql
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);
-- Uses index, milliseconds
```

### Polymorphic Associations (Type columns)

❌ Bad: Violates FK constraint
```sql
CREATE TABLE comments (
    id SERIAL,
    commentable_type VARCHAR(50),
    commentable_id INTEGER
    -- No FK: can reference non-existent post
);
```

✅ Good: Separate tables
```sql
CREATE TABLE post_comments (
    id SERIAL,
    post_id INTEGER REFERENCES posts(id)
);

CREATE TABLE photo_comments (
    id SERIAL,
    photo_id INTEGER REFERENCES photos(id)
);
```

### Storing Computed Values

❌ Bad: Redundant data
```sql
CREATE TABLE orders (
    id SERIAL,
    item_price DECIMAL,
    quantity INTEGER,
    total DECIMAL  -- Can be computed, risk of inconsistency
);
```

✅ Good: Computed on query
```sql
CREATE TABLE orders (
    id SERIAL,
    item_price DECIMAL,
    quantity INTEGER
);

SELECT id, item_price, quantity, (item_price * quantity) as total
FROM orders;
```

### No Constraints

❌ Bad: Trust application
```sql
CREATE TABLE users (
    id SERIAL,
    username VARCHAR(100),
    email VARCHAR(255)
);

-- Application should validate, but what if bug?
```

✅ Good: Database enforces
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    age INTEGER CHECK (age >= 18)
);

-- Invalid data rejected at DB level
```

### Unbounded Date Range

❌ Bad: No retention
```sql
CREATE TABLE logs (
    id SERIAL,
    message TEXT,
    created_at TIMESTAMP
);

-- Table grows forever, no archival strategy
```

✅ Good: Partitioned + Archival
```sql
CREATE TABLE logs (
    id SERIAL,
    message TEXT,
    created_at TIMESTAMP
) PARTITION BY RANGE (DATE_TRUNC('month', created_at));

-- Archive old partitions
CREATE TABLE logs_archive PARTITION OF logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Move to separate storage, compress
```

## Design Checklist

- [ ] Normalized to 3NF minimum
- [ ] Primary keys on all tables
- [ ] Foreign keys for relationships
- [ ] Constraints: NOT NULL, UNIQUE, CHECK
- [ ] Audit trail for critical tables
- [ ] Soft delete for sensitive data
- [ ] Indexes on WHERE/JOIN columns
- [ ] No redundant computed columns
- [ ] Partitioning for large tables (>100M)
- [ ] Retention policy for logs/old data

---

See **PERFORMANCE.md** for optimization strategies.

