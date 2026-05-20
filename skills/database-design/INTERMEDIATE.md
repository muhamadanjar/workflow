# PostgreSQL Intermediate

Joins, subqueries, CTEs, window functions, advanced queries.

## Joins

### INNER JOIN (Records in both tables)

```sql
-- Basic
SELECT u.id, u.username, p.title
FROM users u
INNER JOIN posts p ON u.id = p.user_id;

-- Multiple joins
SELECT 
    u.username,
    p.title,
    c.content
FROM users u
INNER JOIN posts p ON u.id = p.user_id
INNER JOIN comments c ON p.id = c.post_id;

-- Self-join (table joins itself)
SELECT 
    e1.name as employee,
    e2.name as manager
FROM employees e1
INNER JOIN employees e2 ON e1.manager_id = e2.id;
```

### LEFT JOIN (All from left, matching from right)

```sql
-- Include users with no posts
SELECT u.id, u.username, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id, u.username;

-- Find users with no posts
SELECT u.id, u.username
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
WHERE p.id IS NULL;
```

### RIGHT JOIN (All from right, matching from left)

```sql
-- Include posts even if user deleted
SELECT u.username, p.title
FROM users u
RIGHT JOIN posts p ON u.id = p.user_id;

-- Equivalent to: SELECT ... FROM posts p LEFT JOIN users u
```

### FULL OUTER JOIN (All from both)

```sql
-- Include unmatched from both sides
SELECT 
    COALESCE(u.username, 'Unknown') as username,
    COALESCE(p.title, 'No post') as title
FROM users u
FULL OUTER JOIN posts p ON u.id = p.user_id;
```

### CROSS JOIN (Cartesian product)

```sql
-- Every user with every category
SELECT u.username, c.name
FROM users u
CROSS JOIN categories c;

-- Find all possible pairs
SELECT e1.name, e2.name
FROM employees e1
CROSS JOIN employees e2
WHERE e1.id < e2.id;
```

## Subqueries

### In WHERE Clause

```sql
-- Find users with posts
SELECT * FROM users
WHERE id IN (SELECT DISTINCT user_id FROM posts);

-- Find expensive products
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- Find users who bought in last month
SELECT * FROM users
WHERE id IN (
    SELECT DISTINCT user_id FROM orders
    WHERE created_at > NOW() - INTERVAL '30 days'
);

-- NOT IN (opposite)
SELECT * FROM users
WHERE id NOT IN (SELECT user_id FROM posts);
```

### In FROM Clause (Derived table)

```sql
-- Subquery as table
SELECT username, post_count
FROM (
    SELECT u.id, u.username, COUNT(p.id) as post_count
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username
) user_stats
WHERE post_count > 5;

-- Multiple levels
SELECT * FROM (
    SELECT * FROM (
        SELECT id, username FROM users WHERE age > 18
    ) adults
    WHERE username LIKE 'J%'
) j_adults;
```

### Scalar Subquery (Returns single value)

```sql
-- Get user with post count
SELECT 
    id,
    username,
    (SELECT COUNT(*) FROM posts WHERE user_id = users.id) as post_count
FROM users;

-- Get last post date
SELECT 
    id,
    username,
    (SELECT MAX(created_at) FROM posts WHERE user_id = users.id) as last_post
FROM users;
```

### EXISTS / NOT EXISTS

```sql
-- Efficient check for existence
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM posts WHERE user_id = u.id
);

-- Find users with no comments
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM comments c 
    WHERE c.user_id = u.id
);
```

## Common Table Expressions (CTE)

### WITH Clause

```sql
-- Simple CTE
WITH post_counts AS (
    SELECT user_id, COUNT(*) as post_count
    FROM posts
    GROUP BY user_id
)
SELECT u.username, pc.post_count
FROM users u
LEFT JOIN post_counts pc ON u.id = pc.user_id;

-- Multiple CTEs
WITH 
user_posts AS (
    SELECT user_id, COUNT(*) as post_count
    FROM posts
    GROUP BY user_id
),
user_comments AS (
    SELECT user_id, COUNT(*) as comment_count
    FROM comments
    GROUP BY user_id
)
SELECT 
    u.username,
    COALESCE(up.post_count, 0) as posts,
    COALESCE(uc.comment_count, 0) as comments
FROM users u
LEFT JOIN user_posts up ON u.id = up.user_id
LEFT JOIN user_comments uc ON u.id = uc.user_id;
```

### Recursive CTE (Hierarchical data)

```sql
-- Find all descendants of category
WITH RECURSIVE category_tree AS (
    -- Anchor: start with parent category
    SELECT id, name, parent_id, 1 as depth
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive: join child categories
    SELECT c.id, c.name, c.parent_id, ct.depth + 1
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_id = ct.id
    WHERE ct.depth < 10  -- Prevent infinite loop
)
SELECT * FROM category_tree;

-- Find employee hierarchy
WITH RECURSIVE employee_tree AS (
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL  -- Root (CEO)
    
    UNION ALL
    
    SELECT e.id, e.name, e.manager_id, et.level + 1
    FROM employees e
    INNER JOIN employee_tree et ON e.manager_id = et.id
    WHERE et.level < 5
)
SELECT REPEAT('  ', level - 1) || name as employee
FROM employee_tree
ORDER BY id;
```

## Window Functions

Operate on rows related to current row.

### ROW_NUMBER, RANK, DENSE_RANK

```sql
-- Row number (unique position)
SELECT 
    user_id,
    amount,
    ROW_NUMBER() OVER (ORDER BY amount DESC) as rn
FROM transactions;

-- Rank (same rank for ties, skip numbers)
SELECT 
    player,
    score,
    RANK() OVER (ORDER BY score DESC) as rank
FROM leaderboard;

-- Dense rank (no gaps)
SELECT 
    player,
    score,
    DENSE_RANK() OVER (ORDER BY score DESC) as rank
FROM leaderboard;
```

### PARTITION BY

```sql
-- Rank within each department
SELECT 
    name,
    department_id,
    salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_salary_rank
FROM employees;

-- Row number per category
SELECT 
    id,
    category,
    amount,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY amount DESC) as category_rank
FROM products;
```

### LAG, LEAD (Previous/Next row)

```sql
-- Compare with previous value
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) as prev_revenue,
    revenue - LAG(revenue) OVER (ORDER BY month) as growth
FROM monthly_sales;

-- Look ahead
SELECT 
    order_date,
    amount,
    LEAD(amount) OVER (ORDER BY order_date) as next_amount
FROM orders;

-- Partition by user
SELECT 
    user_id,
    date,
    balance,
    LAG(balance) OVER (PARTITION BY user_id ORDER BY date) as prev_balance
FROM account_history;
```

### Aggregate Over Window

```sql
-- Running total
SELECT 
    month,
    amount,
    SUM(amount) OVER (ORDER BY month) as cumulative
FROM transactions;

-- Moving average (3-month)
SELECT 
    month,
    revenue,
    AVG(revenue) OVER (
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as moving_avg
FROM monthly_sales;

-- Percent of total
SELECT 
    category,
    amount,
    100.0 * amount / SUM(amount) OVER () as percent_of_total
FROM sales;
```

### FIRST_VALUE, LAST_VALUE

```sql
-- First and last order by user
SELECT 
    user_id,
    order_date,
    amount,
    FIRST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY order_date) as first_amount,
    LAST_VALUE(amount) OVER (
        PARTITION BY user_id 
        ORDER BY order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_amount
FROM orders;
```

## Set Operations

### UNION (All + Remove duplicates)

```sql
-- Combine results
SELECT username as name FROM users
UNION
SELECT company_name as name FROM companies;

-- UNION ALL (keep duplicates)
SELECT username FROM users
UNION ALL
SELECT username FROM archived_users;
```

### INTERSECT (Rows in both)

```sql
-- Users who are both staff and customers
SELECT user_id FROM staff_members
INTERSECT
SELECT user_id FROM customers;
```

### EXCEPT (Rows in first but not second)

```sql
-- Users who never made a purchase
SELECT id FROM users
EXCEPT
SELECT DISTINCT user_id FROM orders;
```

## Advanced Filtering

### FILTER Clause

```sql
-- Conditional aggregation (clean)
SELECT 
    department_id,
    COUNT(*) FILTER (WHERE salary > 50000) as high_earners,
    COUNT(*) FILTER (WHERE salary <= 50000) as low_earners,
    COUNT(*) as total
FROM employees
GROUP BY department_id;
```

### CASE in SELECT

```sql
-- Categorize results
SELECT 
    username,
    CASE 
        WHEN age < 18 THEN 'Minor'
        WHEN age < 65 THEN 'Adult'
        ELSE 'Senior'
    END as age_group,
    CASE 
        WHEN status = 'premium' THEN salary * 1.2
        ELSE salary
    END as adjusted_salary
FROM users;
```

### IN with Ranges

```sql
-- Between shorthand
SELECT * FROM orders
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';

-- Multiple conditions
SELECT * FROM products
WHERE category IN ('Electronics', 'Books', 'Toys')
AND price BETWEEN 10 AND 100;
```

## String Operations

```sql
-- Concatenation
SELECT username || '@example.com' as email FROM users;

-- Case conversion
SELECT UPPER(username) FROM users;
SELECT LOWER(email) FROM users;

-- Pattern matching
SELECT * FROM users WHERE username ILIKE 'john%';  -- Case-insensitive
SELECT * FROM users WHERE email ~ '^[a-z]+@' ;    -- Regex

-- String functions
SELECT 
    SUBSTRING(username, 1, 3) as prefix,
    LENGTH(username) as name_length,
    TRIM(description) as cleaned,
    REPLACE(email, '@example.com', '@newdomain.com') as new_email
FROM users;

-- Split string
SELECT UNNEST(STRING_TO_ARRAY(tags, ',')) as tag
FROM posts;
```

## Date Functions

```sql
-- Extract components
SELECT 
    EXTRACT(YEAR FROM created_at) as year,
    EXTRACT(MONTH FROM created_at) as month,
    EXTRACT(DAY FROM created_at) as day
FROM posts;

-- Date arithmetic
SELECT 
    created_at,
    created_at + INTERVAL '30 days' as due_date,
    NOW() - created_at as age
FROM invoices;

-- Date truncation
SELECT DATE_TRUNC('month', created_at) as month_start
FROM sales;

-- Age calculation
SELECT username, AGE(NOW(), birth_date) as age
FROM users;
```

## Performance Considerations

### Query Plans

```sql
-- See query execution plan
EXPLAIN SELECT * FROM users WHERE age > 25;

-- Detailed plan with execution
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 25;

-- See statistics
ANALYZE users;
```

### Index Benefits

```sql
-- Without index: Sequential scan (slow)
SELECT * FROM users WHERE email = 'test@example.com';

-- Create index: Use index scan (fast)
CREATE INDEX idx_users_email ON users(email);

-- Now same query uses index
SELECT * FROM users WHERE email = 'test@example.com';
```

## Checklist

- [ ] Correct join type used (INNER/LEFT/RIGHT/FULL)
- [ ] WHERE clause filters before JOIN (performance)
- [ ] Subqueries in proper scope (SELECT/FROM/WHERE)
- [ ] CTE used for readability (complex queries)
- [ ] Recursive CTE has termination condition
- [ ] Window functions use correct PARTITION BY
- [ ] Aggregate functions use GROUP BY correctly
- [ ] Set operations use compatible columns
- [ ] Indexes support WHERE conditions
- [ ] Query plan reviewed with EXPLAIN ANALYZE

---

See **ADVANCED.md** for stored procedures, triggers, optimization.

