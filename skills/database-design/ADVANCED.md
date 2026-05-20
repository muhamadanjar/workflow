# PostgreSQL Advanced

Stored procedures, triggers, transactions, advanced optimization.

## Stored Procedures

PL/pgSQL: SQL procedural language.

### Basic Procedure

```sql
-- Create procedure (no return)
CREATE PROCEDURE add_user(
    p_username VARCHAR,
    p_email VARCHAR,
    p_age INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (username, email, age)
    VALUES (p_username, p_email, p_age);
    COMMIT;
END;
$$;

-- Call procedure
CALL add_user('john', 'john@example.com', 30);
```

### Function (Returns value)

```sql
-- Create function
CREATE FUNCTION get_user_post_count(p_user_id INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM posts
    WHERE user_id = p_user_id;
    
    RETURN v_count;
END;
$$;

-- Use in query
SELECT username, get_user_post_count(id) as posts
FROM users;
```

### Function with Multiple Statements

```sql
-- Create user and return ID
CREATE FUNCTION create_user_with_profile(
    p_username VARCHAR,
    p_email VARCHAR
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id INTEGER;
BEGIN
    -- Insert user
    INSERT INTO users (username, email)
    VALUES (p_username, p_email)
    RETURNING id INTO v_user_id;
    
    -- Create profile
    INSERT INTO user_profiles (user_id, bio)
    VALUES (v_user_id, '');
    
    -- Return user ID
    RETURN v_user_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Username already exists: %', p_username;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error: %', SQLERRM;
END;
$$;

-- Call
SELECT create_user_with_profile('john', 'john@example.com');
```

### Procedure with Loop

```sql
-- Process data in bulk
CREATE PROCEDURE archive_old_posts(p_days_old INTEGER DEFAULT 365)
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
BEGIN
    -- Move old posts to archive
    INSERT INTO posts_archive
    SELECT * FROM posts
    WHERE created_at < NOW() - (p_days_old || ' days')::INTERVAL;
    
    -- Delete from main table
    DELETE FROM posts
    WHERE created_at < NOW() - (p_days_old || ' days')::INTERVAL;
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Archived % posts', v_count;
    
    COMMIT;
END;
$$;

-- Call
CALL archive_old_posts(365);
```

### Procedure with Cursor

```sql
-- Process each row individually
CREATE PROCEDURE process_user_data()
LANGUAGE plpgsql
AS $$
DECLARE
    user_record RECORD;
    v_cursor CURSOR FOR SELECT id, username, email FROM users WHERE status = 'inactive';
BEGIN
    OPEN v_cursor;
    
    LOOP
        FETCH v_cursor INTO user_record;
        EXIT WHEN NOT FOUND;
        
        -- Process each user
        UPDATE user_profiles SET status = 'archived'
        WHERE user_id = user_record.id;
        
        -- Could send email, etc.
        RAISE NOTICE 'Processed user: %', user_record.username;
    END LOOP;
    
    CLOSE v_cursor;
    COMMIT;
END;
$$;

-- Call
CALL process_user_data();
```

## Triggers

Automatic actions on INSERT/UPDATE/DELETE.

### Basic Trigger

```sql
-- Update timestamp on every update
CREATE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER users_updated_at_trigger
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Now every UPDATE automatically sets updated_at
UPDATE users SET email = 'new@example.com' WHERE id = 1;
-- updated_at automatically becomes NOW()
```

### Audit Trigger

```sql
-- Log all changes to audit table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(10),
    record_id INTEGER,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100)
);

CREATE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data, changed_by)
        VALUES (TG_TABLE_NAME, 'INSERT', NEW.id, NULL, row_to_json(NEW), CURRENT_USER);
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data, changed_by)
        VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id, row_to_json(OLD), row_to_json(NEW), CURRENT_USER);
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data, changed_by)
        VALUES (TG_TABLE_NAME, 'DELETE', OLD.id, row_to_json(OLD), NULL, CURRENT_USER);
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply to users table
CREATE TRIGGER users_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION audit_trigger();

-- View audit log
SELECT * FROM audit_log ORDER BY changed_at DESC;
```

### Validation Trigger

```sql
-- Validate data on insert/update
CREATE FUNCTION validate_product()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price <= 0 THEN
        RAISE EXCEPTION 'Price must be positive';
    END IF;
    
    IF NEW.stock < 0 THEN
        RAISE EXCEPTION 'Stock cannot be negative';
    END IF;
    
    IF NEW.name IS NULL OR NEW.name = '' THEN
        RAISE EXCEPTION 'Name is required';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_validate_trigger
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION validate_product();
```

### Cascade Trigger (Update related rows)

```sql
-- When user is deleted, soft-delete posts
CREATE FUNCTION cascade_delete_posts()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE posts SET deleted_at = CURRENT_TIMESTAMP
    WHERE user_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_delete_cascade
AFTER DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION cascade_delete_posts();
```

## Transactions

ACID guarantees.

### Explicit Transaction

```sql
-- All or nothing
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- If any error, rollback entire transaction
BEGIN;
    INSERT INTO orders (user_id, total) VALUES (1, 500);
    INSERT INTO order_items (order_id, product_id, qty) VALUES (999, 1, 1);  -- Error: order_id doesn't exist
ROLLBACK;
-- Both inserts undone
```

### Savepoint (Partial rollback)

```sql
BEGIN;
    INSERT INTO users (username) VALUES ('john');
    SAVEPOINT sp1;
    
    INSERT INTO profiles (username) VALUES ('invalid');  -- Error
    
    ROLLBACK TO sp1;  -- Undo profile insert, keep user insert
    
    INSERT INTO profiles (username) VALUES ('valid');
COMMIT;
```

### Isolation Levels

```sql
-- Read Uncommitted (lowest isolation, highest concurrency)
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- Read Committed (default, prevents dirty reads)
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Repeatable Read (prevents phantom reads)
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Serializable (highest isolation, like serial execution)
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Usage
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
    SELECT * FROM users WHERE id = 1;
    -- Other transaction can't change this row
COMMIT;
```

### Deadlock Prevention

```sql
-- Order locks consistently (A→B order)
-- Transaction 1
BEGIN;
    SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
    SELECT * FROM accounts WHERE id = 2 FOR UPDATE;
    -- Update both
COMMIT;

-- Transaction 2 (same order)
BEGIN;
    SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
    SELECT * FROM accounts WHERE id = 2 FOR UPDATE;
    -- Update both
COMMIT;

-- Prevents deadlock from circular waits
```

## Window Functions Advanced

### Numbered Partitions

```sql
-- Assign group numbers
SELECT 
    id,
    status,
    ROW_NUMBER() OVER (ORDER BY created_at) as global_row,
    ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at) as status_row
FROM orders;

-- Gaps and islands (find consecutive groups)
WITH numbered AS (
    SELECT 
        id,
        status,
        ROW_NUMBER() OVER (ORDER BY created_at) as rn,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at) as status_rn
    FROM orders
)
SELECT 
    status,
    MIN(id) as start_id,
    MAX(id) as end_id,
    COUNT(*) as consecutive_count
FROM numbered
GROUP BY status, (rn - status_rn)
ORDER BY status, start_id;
```

## JSON Operations

```sql
-- Store structured data
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    profile JSONB  -- Better than JSON: indexed, searchable
);

-- Insert JSON
INSERT INTO users (username, profile) VALUES (
    'john',
    '{"age": 30, "city": "NYC", "hobbies": ["coding", "gaming"]}'::jsonb
);

-- Query JSON
SELECT username, profile->>'age' as age FROM users;  -- Extract string
SELECT username, profile->'hobbies'->0 as first_hobby FROM users;  -- Extract array element
SELECT username, profile@>'{"city": "NYC"}' as in_nyc FROM users;  -- Contains check

-- Extract as table
SELECT 
    username,
    hobby
FROM users,
LATERAL JSONB_ARRAY_ELEMENTS_TEXT(profile->'hobbies') as hobby;
```

## Partitioning

Large tables split into smaller parts.

### Range Partitioning

```sql
-- Partition by date range
CREATE TABLE orders (
    id SERIAL,
    user_id INTEGER,
    amount DECIMAL,
    created_at DATE,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (EXTRACT(YEAR FROM created_at));

CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM (2023) TO (2024);

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM (2024) TO (2025);

-- Insert automatically goes to correct partition
INSERT INTO orders VALUES (1, 1, 100.00, '2023-06-15');  -- Goes to orders_2023
INSERT INTO orders VALUES (2, 1, 150.00, '2024-06-15');  -- Goes to orders_2024
```

## Optimization Techniques

### Index Strategies

```sql
-- Multiple-column index (for WHERE + ORDER BY)
CREATE INDEX idx_posts_user_date ON posts(user_id, created_at DESC);

-- Partial index (indexed rows only)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Expression index
CREATE INDEX idx_lower_email ON users(LOWER(email));

-- Full-text search index
CREATE INDEX idx_search ON articles USING gin(to_tsvector('english', title || ' ' || content));
```

### Query Optimization

```sql
-- Use EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT u.username, COUNT(p.id) as posts
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id, u.username;

-- Add index if needed
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- Re-run EXPLAIN to verify improvement
```

### Materialized Views

```sql
-- Pre-compute expensive query
CREATE MATERIALIZED VIEW user_stats_mv AS
SELECT 
    u.id,
    u.username,
    COUNT(p.id) as post_count,
    COUNT(DISTINCT c.id) as comment_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
LEFT JOIN comments c ON p.id = c.post_id
GROUP BY u.id, u.username;

-- Refresh when data changes
REFRESH MATERIALIZED VIEW user_stats_mv;

-- Query is now fast
SELECT * FROM user_stats_mv;
```

## Checklist

- [ ] Stored procedures for complex business logic
- [ ] Triggers for audit logging
- [ ] Triggers for cascading updates
- [ ] Transactions for multi-step operations
- [ ] Proper isolation level set
- [ ] Deadlock prevention (consistent lock order)
- [ ] Indexes on frequently queried columns
- [ ] Query plans reviewed (EXPLAIN ANALYZE)
- [ ] Partitioning for large tables (>100M rows)
- [ ] Materialized views for expensive queries

---

See **PATTERNS.md** for design patterns and anti-patterns.

