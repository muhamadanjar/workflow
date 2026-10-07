# Authentication & Authorization Patterns

## JWT (JSON Web Token)

### Token Structure
```
Header.Payload.Signature

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### JWT Payload
```json
{
  "sub": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "roles": ["user", "admin"],
  "iat": 1516239022,
  "exp": 1516325422
}
```

### Issuing JWT
```python
import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: str, expires_delta: timedelta = None):
    data = {
        "sub": user_id,
        "iat": datetime.utcnow(),
    }
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    
    data["exp"] = expire
    
    token = jwt.encode(data, SECRET_KEY, algorithm="HS256")
    return token
```

### Verifying JWT
```python
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
    return user_id
```

## OAuth 2.0

### Authorization Code Flow
```
1. User clicks "Login with Google"
2. Redirect to: https://accounts.google.com/o/oauth2/auth?
   client_id=xxx&redirect_uri=http://myapp.com/callback&...
3. Google asks user for permission
4. Google redirects back: http://myapp.com/callback?code=abc123
5. Backend exchanges code for token:
   POST https://oauth2.googleapis.com/token
   code=abc123&client_id=xxx&client_secret=yyy
6. Receive access token
7. Use token to access Google APIs
```

### Implementation (Python)
```python
from authlib.integrations.flask_client import OAuth

oauth = OAuth()
google = oauth.register(
    name='google',
    client_id='xxx',
    client_secret='yyy',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/login')
def login():
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    token = google.authorize_access_token()
    user = token['userinfo']
    # Create user session
    return redirect('/')
```

## API Key Authentication

```python
from fastapi import Header, HTTPException

def verify_api_key(x_api_key: str = Header(...)):
    if not is_valid_api_key(x_api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

@app.get("/data")
def get_data(api_key: str = Depends(verify_api_key)):
    return {"data": "..."}
```

## Bearer Token in Header

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

```python
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    user_id = verify_jwt(token)
    if not user_id:
        raise HTTPException(status_code=403)
    return user_id
```

## Role-Based Access Control (RBAC)

```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

def has_permission(required_roles: List[Role]):
    def check_permission(user: User = Depends(get_current_user)):
        if user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return check_permission

@app.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    user: User = Depends(has_permission([Role.ADMIN]))
):
    # Only admins can delete
    return {"deleted": user_id}
```

## Attribute-Based Access Control (ABAC)

```python
def can_edit_post(user: User, post: Post) -> bool:
    # User can edit if they're author or admin
    return user.id == post.author_id or user.role == Role.ADMIN

def can_delete_post(user: User, post: Post) -> bool:
    # Only admins or user with high reputation
    return user.role == Role.ADMIN or user.reputation > 1000

@app.put("/posts/{post_id}")
def update_post(
    post_id: str,
    updated_data: dict,
    user: User = Depends(get_current_user)
):
    post = get_post(post_id)
    if not can_edit_post(user, post):
        raise HTTPException(status_code=403)
    # Update post
```

## Refresh Tokens

```python
def create_token_pair(user_id: str):
    access_token = create_jwt(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=15)
    )
    
    refresh_token = create_jwt(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=7)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@app.post("/token/refresh")
def refresh_access_token(refresh_token: str):
    user_id = verify_token(refresh_token)
    if not user_id:
        raise HTTPException(status_code=403)
    
    new_access_token = create_jwt(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=15)
    )
    
    return {"access_token": new_access_token}
```

## Session-Based Authentication

```python
from flask import session

@app.route('/login', methods=['POST'])
def login():
    user = authenticate_user(request.json['email'], request.json['password'])
    if not user:
        return {"error": "Invalid credentials"}, 401
    
    session['user_id'] = user.id
    session['user_role'] = user.role
    return {"success": True}

@app.route('/protected')
def protected():
    if 'user_id' not in session:
        return {"error": "Not authenticated"}, 401
    
    user_id = session['user_id']
    return {"data": f"User {user_id} data"}
```

## Best Practices

- ✅ Always use HTTPS for auth endpoints
- ✅ Hash passwords with bcrypt/argon2
- ✅ Use refresh tokens for long-lived sessions
- ✅ Set reasonable token expiration times
- ✅ Validate all inputs
- ✅ Log authentication events
- ✅ Implement rate limiting on auth endpoints
- ✅ Never store tokens in localStorage (use httpOnly cookies)
- ✅ Implement CSRF protection for form-based auth
- ✅ Use SameSite cookie attribute
