# PostgreSQL Security

SQL injection prevention, access control, row-level security (RLS).

## SQL Injection Prevention

### Parameterized Queries (Prepared Statements)

❌ Bad: String concatenation (SQL injection risk)

```python
# Vulnerable to SQL injection
user_id = "1'; DROP TABLE users; --"
query = f"SELECT * FROM users WHERE id = {user_id}"
# Executes: SELECT * FROM users WHERE id = 1'; DROP TABLE users; --

db.execute(query)  # Disaster!
```

✅ Good: Parameterized query

```python
# Safe: Parameter is data, not code
user_id = "1'; DROP TABLE users; --"
query = "SELECT * FROM users WHERE id = %s"
db.execute(query, (user_id,))
# Executes: SELECT * FROM users WHERE id = '1''; DROP TABLE users; --'
# Treated as string literal, not executed
```

### Examples in Different Languages

```python
# Python (psycopg2)
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# Python (SQLAlchemy)
result = db.session.execute(
    select(User).where(User.email == email)
)

# Node.js (pg)
client.query("SELECT * FROM users WHERE email = $1", [email])

# Java (JDBC)
PreparedStatement pstmt = conn.prepareStatement("SELECT * FROM users WHERE email = ?");
pstmt.setString(1, email);
ResultSet rs = pstmt.executeQuery();

# PHP (PDO)
$stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
$stmt->execute([$email]);

# Ruby (ActiveRecord)
User.where(email: email)
```

### Input Validation

```python
# Always validate input type and range
def get_user(user_id):
    # Validate type
    if not isinstance(user_id, int):
        raise ValueError("user_id must be integer")
    
    # Validate range
    if user_id <= 0 or user_id > 999999999:
        raise ValueError("user_id out of range")
    
    # Now safe to use in query
    return db.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Escaping (Last Resort)

```sql
-- Quote_literal() escapes strings
SELECT * FROM users WHERE username = quote_literal('user''s name');
-- Becomes: SELECT * FROM users WHERE username = 'user''s name';

-- Use only when parameterized queries not possible
-- Prefer parameterized queries always!
```

## Access Control

### Role-Based Access

```sql
-- Create roles
CREATE ROLE app_user LOGIN PASSWORD 'password' VALID UNTIL '2026-01-01';
CREATE ROLE app_admin LOGIN PASSWORD 'password';
CREATE ROLE readonly;

-- Grant permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO app_admin;

-- Grant to specific table
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
GRANT DELETE ON users TO app_admin;

-- Revoke permission
REVOKE INSERT ON users FROM readonly;

-- Check permissions
\du           -- List roles
\dp users     -- List permissions on users table
```

### Role Hierarchy

```sql
-- Inherit permissions from parent role
CREATE ROLE admin;
CREATE ROLE senior_admin ROLE admin;  -- Inherits from admin
CREATE ROLE junior_admin ROLE admin;  -- Inherits from admin

-- senior_admin and junior_admin inherit admin's permissions
```

### Schema-Level Access

```sql
-- Grant all permissions on schema
GRANT ALL ON SCHEMA app TO app_user;
GRANT USAGE ON SCHEMA app TO readonly;

-- Control table creation in schema
GRANT CREATE ON SCHEMA app TO app_admin;
REVOKE CREATE ON SCHEMA app FROM app_user;
```

## Row-Level Security (RLS)

Restrict data access per user/role.

### Basic RLS Policy

```sql
-- Add RLS policy
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own row
CREATE POLICY users_self_policy ON users
    FOR SELECT
    USING (id = CURRENT_USER_ID());  -- Assuming custom function

-- Create function to get current user ID
CREATE OR REPLACE FUNCTION CURRENT_USER_ID()
RETURNS INTEGER AS $$
BEGIN
    RETURN (current_setting('app.current_user_id'))::INTEGER;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Set user ID in application
SET app.current_user_id = '123';

-- Now queries automatically filter
SELECT * FROM users;  -- Only returns user 123's row
```

### Multiple Policies

```sql
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- SELECT: Users see own posts + public posts
CREATE POLICY posts_select_policy ON posts
    FOR SELECT
    USING (
        user_id = CURRENT_USER_ID() OR is_public = true
    );

-- INSERT: Users can only insert their own posts
CREATE POLICY posts_insert_policy ON posts
    FOR INSERT
    WITH CHECK (user_id = CURRENT_USER_ID());

-- UPDATE: Users can only update their own posts
CREATE POLICY posts_update_policy ON posts
    FOR UPDATE
    USING (user_id = CURRENT_USER_ID())
    WITH CHECK (user_id = CURRENT_USER_ID());

-- DELETE: Only admins can delete
CREATE POLICY posts_delete_policy ON posts
    FOR DELETE
    USING (has_admin_role());
```

### RLS for Multi-Tenant

```sql
-- Company-specific data
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY documents_tenant_policy ON documents
    FOR ALL
    USING (
        company_id = (
            SELECT company_id FROM users WHERE id = CURRENT_USER_ID()
        )
    );

-- Users only see documents from their company
SET app.current_user_id = '123';  -- App sets this
SELECT * FROM documents;  -- Only company's documents
```

## Data Encryption

### Column Encryption

```sql
-- Encrypt sensitive columns
CREATE EXTENSION pgcrypto;

-- Encrypt data
INSERT INTO users (username, email, encrypted_password)
VALUES ('john', 'john@example.com', pgp_sym_encrypt('password123', 'secret_key'));

-- Decrypt
SELECT username, pgp_sym_decrypt(encrypted_password, 'secret_key')
FROM users
WHERE id = 1;

-- One-way hash (no decryption)
INSERT INTO users (username, password_hash)
VALUES ('john', crypt('password123', gen_salt('bf')));

-- Verify password
SELECT username FROM users
WHERE username = 'john' AND password_hash = crypt('password123', password_hash);
```

### Transport Encryption

```bash
# Force SSL connections (postgresql.conf)
ssl = on
ssl_cert_file = '/etc/ssl/cert.pem'
ssl_key_file = '/etc/ssl/key.pem'

# Client connection with SSL
psql -h postgres.example.com -U user -d mydb --set=sslmode=require

# In application
conn_string = "postgresql://user:pass@host:5432/db?sslmode=require"
```

## Audit Trail

### Log All Changes

```sql
-- Create audit log table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(10),
    record_id INTEGER,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100),
    ip_address INET
);

-- Audit trigger
CREATE FUNCTION audit_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data, changed_by, ip_address)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW) ELSE NULL END,
        CURRENT_USER,
        inet_client_addr()
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply to sensitive tables
CREATE TRIGGER users_audit AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_function();

CREATE TRIGGER payments_audit AFTER INSERT OR UPDATE OR DELETE ON payments
FOR EACH ROW EXECUTE FUNCTION audit_function();

-- Query audit log
SELECT * FROM audit_log ORDER BY changed_at DESC;
```

## Secure Configuration

### postgresql.conf

```ini
# Disable superuser login
# (Create limited user instead)
# superuser cannot be disabled, but restrict its use

# Force password authentication
password_encryption = scram-sha-256  # Never use md5

# SSL
ssl = on
ssl_cert_file = '/path/to/cert.pem'
ssl_key_file = '/path/to/key.pem'

# Logging
log_connections = on
log_disconnections = on
log_statement = 'all'  # Log all queries (disable in production)
log_min_duration_statement = 1000  # Log slow queries > 1 second

# Security
check_function_bodies = on  # Validate function SQL
```

### pg_hba.conf (Host-Based Authentication)

```conf
# Allow local connections (socket)
local   all             all                                     trust

# Require SSL for remote connections
hostssl all             all             0.0.0.0/0               scram-sha-256

# Reject unencrypted remote
hostnossl all           all             0.0.0.0/0               reject

# Specific user/database rules
host    myapp           app_user        192.168.1.0/24          scram-sha-256
host    myapp           app_admin       192.168.1.0/24          scram-sha-256
```

## Vulnerability Checklist

- [ ] All queries use parameterized statements (never string concatenation)
- [ ] Input validation on type and range
- [ ] Roles created with least privilege
- [ ] Sensitive tables have RLS enabled
- [ ] Password hashing with strong algorithm (bcrypt, scram-sha-256)
- [ ] Passwords never logged
- [ ] Sensitive columns encrypted
- [ ] SSL enabled for network connections
- [ ] pg_hba.conf restricts access
- [ ] Audit logging for sensitive operations
- [ ] Regular backups encrypted at rest
- [ ] Database regularly patched

---

## Example: Secure Application Code

```python
import psycopg2
from functools import wraps

class SecureDB:
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(
            connection_string,
            sslmode='require'  # Require SSL
        )
    
    def query(self, sql, params=None):
        """Execute parameterized query"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_user(self, user_id):
        """Example: Safe user fetch"""
        # Validate input
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Invalid user_id")
        
        # Parameterized query (safe)
        return self.query(
            "SELECT id, username, email FROM users WHERE id = %s",
            (user_id,)
        )
    
    def login(self, username, password):
        """Secure authentication"""
        # Parameterized query
        result = self.query(
            "SELECT id, password_hash FROM users WHERE username = %s",
            (username,)
        )
        
        if not result:
            raise ValueError("Invalid credentials")
        
        user_id, password_hash = result[0]
        
        # Check password (one-way hash, no decryption)
        if not self.verify_password(password, password_hash):
            raise ValueError("Invalid credentials")
        
        return user_id
    
    def verify_password(self, plain, hashed):
        """Verify password using database function"""
        result = self.query(
            "SELECT crypt(%s, %s) = %s",
            (plain, hashed, hashed)
        )
        return result[0][0] if result else False

# Usage
db = SecureDB("postgresql://user:pass@localhost/myapp?sslmode=require")

# Safe
user = db.get_user(123)

# Also safe (SQL injection prevented)
user = db.get_user("123; DROP TABLE users; --")  # Rejected as int
```

---

See **EXAMPLES.md** for complete schemas.

