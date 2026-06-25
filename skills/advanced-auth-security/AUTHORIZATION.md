# Authorization Patterns

## RBAC (Role-Based Access Control)

```python
class Permission:
    def __init__(self, roles):
        self.roles = roles
    
    def check(self, user_roles):
        return any(role in self.roles for role in user_roles)

def require_role(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_user = get_current_user()
            if not any(r in current_user.roles for r in roles):
                raise PermissionError('Insufficient permissions')
            return func(*args, **kwargs)
        return wrapper
    return decorator

@require_role('admin')
def delete_user(user_id):
    db.users.delete(user_id)

@require_role('user', 'admin')
def view_profile(user_id):
    return db.users.findById(user_id)
```

## ABAC (Attribute-Based Access Control)

```python
class Policy:
    def __init__(self, rules):
        self.rules = rules
    
    def evaluate(self, user, resource, action):
        for rule in self.rules:
            if rule.matches(user, resource, action):
                return rule.effect == 'allow'
        return False

policies = [
    # Own posts
    {
        'effect': 'allow',
        'principal': {'type': 'user'},
        'action': ['post:edit', 'post:delete'],
        'resource': 'post:${author_id}',
        'condition': {'equals': ['${user_id}', '${author_id}']}
    },
    # Admin can do anything
    {
        'effect': 'allow',
        'principal': {'role': 'admin'},
        'action': '*',
        'resource': '*'
    }
]
```

## API Key Authorization

```python
# Generate API key
def generate_api_key(user_id):
    key = secrets.token_urlsafe(32)
    hashed = hashlib.sha256(key.encode()).hexdigest()
    
    db.api_keys.insert({
        'user_id': user_id,
        'key_hash': hashed,
        'created_at': datetime.utcnow(),
        'last_used': None
    })
    
    return key

# Validate API key
def validate_api_key(api_key):
    hashed = hashlib.sha256(api_key.encode()).hexdigest()
    key_record = db.api_keys.findOne({'key_hash': hashed})
    
    if not key_record:
        raise Exception('Invalid API key')
    
    # Update last used
    db.api_keys.updateOne({'_id': key_record['_id']}, {
        'last_used': datetime.utcnow()
    })
    
    return key_record['user_id']
```

## Dynamic Permissions

```python
class DynamicPermission:
    def __init__(self):
        self.permissions = {}
    
    def grant(self, user_id, resource, action):
        key = f"{user_id}:{resource}:{action}"
        self.permissions[key] = True
    
    def revoke(self, user_id, resource, action):
        key = f"{user_id}:{resource}:{action}"
        del self.permissions[key]
    
    def has(self, user_id, resource, action):
        key = f"{user_id}:{resource}:{action}"
        return key in self.permissions

# Usage
perm = DynamicPermission()
perm.grant('user1', 'project:123', 'read')
perm.grant('user1', 'project:123', 'edit')

if perm.has('user1', 'project:123', 'edit'):
    # Allow edit
    pass
```

## Best Practices

- ✅ Principle of least privilege
- ✅ Separate auth from authz
- ✅ Use roles for simple cases
- ✅ Use ABAC for complex policies
- ✅ Audit all access decisions
- ✅ Cache permissions efficiently
- ✅ Regular permission reviews
