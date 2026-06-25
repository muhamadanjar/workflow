# JWT Advanced Patterns

## JWT Structure

```
Header.Payload.Signature

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

## Payload Structure

```python
import jwt
from datetime import datetime, timedelta

# Create token
payload = {
    'sub': '123456789',      # Subject (user ID)
    'name': 'John Doe',
    'email': 'john@example.com',
    'iat': datetime.utcnow(),           # Issued at
    'exp': datetime.utcnow() + timedelta(hours=1),  # Expiration
    'nbf': datetime.utcnow(),           # Not before
    'roles': ['user', 'admin']
}

token = jwt.encode(payload, 'secret', algorithm='HS256')
```

## Refresh Token Pattern

```python
class TokenManager:
    def __init__(self, secret, refresh_secret):
        self.secret = secret
        self.refresh_secret = refresh_secret
    
    def create_tokens(self, user_id):
        # Short-lived access token (15 min)
        access_token = jwt.encode({
            'sub': user_id,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }, self.secret, algorithm='HS256')
        
        # Long-lived refresh token (7 days)
        refresh_token = jwt.encode({
            'sub': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=7)
        }, self.refresh_secret, algorithm='HS256')
        
        return access_token, refresh_token
    
    def refresh_access_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.refresh_secret, algorithms=['HS256'])
            
            if payload.get('type') != 'refresh':
                raise Exception('Invalid token type')
            
            return self.create_tokens(payload['sub'])[0]
        except jwt.ExpiredSignatureError:
            raise Exception('Refresh token expired')
```

## Token Rotation

```python
# Store token version in database
class TokenRotation:
    def __init__(self):
        self.token_versions = {}  # user_id -> version
    
    def create_token(self, user_id):
        version = self.token_versions.get(user_id, 0)
        
        token = jwt.encode({
            'sub': user_id,
            'version': version,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, 'secret', algorithm='HS256')
        
        return token
    
    def invalidate_tokens(self, user_id):
        # Increment version to invalidate all tokens
        self.token_versions[user_id] = self.token_versions.get(user_id, 0) + 1
    
    def verify_token(self, token):
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user_id = payload['sub']
        version = payload.get('version', 0)
        
        # Check if token version matches
        if version != self.token_versions.get(user_id, 0):
            raise Exception('Token invalidated')
        
        return payload
```

## Asymmetric Signing (RS256)

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate keys
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

public_key = private_key.public_key()

# Encode/Decode
token = jwt.encode(payload, private_key, algorithm='RS256')
decoded = jwt.decode(token, public_key, algorithms=['RS256'])
```

## Token Validation

```python
def validate_token(token):
    try:
        payload = jwt.decode(
            token,
            'secret',
            algorithms=['HS256'],
            options={
                'verify_signature': True,
                'verify_exp': True,
                'verify_nbf': True,
                'verify_iat': True,
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')
```

## Secure Storage

```javascript
// Client: Store in httpOnly cookie (not localStorage)
// Server sets token in response
res.setHeader('Set-Cookie', `token=${jwt}; HttpOnly; Secure; SameSite=Strict`);

// Never expose token in URL
// ❌ Don't: window.location = `/callback?token=${token}`
// ✅ Do: POST to server, receive httpOnly cookie

// CSRF protection with token
const token = req.cookies.token;
const csrfToken = req.headers['x-csrf-token'];
if (csrfToken !== session.csrfToken) {
    throw new Error('CSRF validation failed');
}
```

## Best Practices

- ✅ Use RS256 for multi-service
- ✅ Keep access token short-lived
- ✅ Use refresh tokens for renewal
- ✅ Rotate signing keys
- ✅ Store in httpOnly cookies
- ✅ Validate all claims
- ✅ Implement token revocation
- ✅ Use HTTPS only
- ✅ Never log tokens
