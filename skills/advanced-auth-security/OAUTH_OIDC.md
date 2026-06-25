# OAuth 2.0 & OpenID Connect

## OAuth 2.0 Authorization Code Flow

```python
# 1. Redirect to provider
authorization_url = f"{PROVIDER_URL}/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid profile email&response_type=code"

# 2. User logs in and grants permission
# Provider redirects to: redirect_uri?code=AUTH_CODE

# 3. Exchange code for token
import requests

response = requests.post(f"{PROVIDER_URL}/token", data={
    'grant_type': 'authorization_code',
    'code': auth_code,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri': REDIRECT_URI
})

token_data = response.json()
access_token = token_data['access_token']

# 4. Use token to get user info
user_info = requests.get(
    f"{PROVIDER_URL}/userinfo",
    headers={'Authorization': f'Bearer {access_token}'}
).json()

# Create/update user
user = db.users.find_or_create(email=user_info['email'])
```

## PKCE (Proof Key for Code Exchange)

```python
import secrets
import hashlib
import base64

# Generate code verifier
code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

# Create code challenge
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode()

# 1. Authorization request with challenge
auth_url = f"{PROVIDER_URL}/authorize?client_id={CLIENT_ID}&code_challenge={code_challenge}&code_challenge_method=S256&redirect_uri={REDIRECT_URI}"

# 2. Token exchange with verifier
token_response = requests.post(f"{PROVIDER_URL}/token", data={
    'grant_type': 'authorization_code',
    'code': auth_code,
    'client_id': CLIENT_ID,
    'code_verifier': code_verifier,
    'redirect_uri': REDIRECT_URI
})
```

## Social Login (Google Example)

```python
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, session

app = Flask(__name__)
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id='GOOGLE_CLIENT_ID',
    client_secret='GOOGLE_CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/login')
def login():
    return google.authorize_redirect(redirect_uri=url_for('authorize', _external=True))

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    user = token.get('userinfo')
    
    session['user'] = {
        'id': user['sub'],
        'email': user['email'],
        'name': user['name']
    }
    
    return redirect('/')
```

## OpenID Connect

```python
# OpenID Connect adds identity layer on top of OAuth
# Includes ID token (JWT) with user info

import jwt

# Decode ID token
id_token = token_data['id_token']
user_claims = jwt.decode(
    id_token,
    options={"verify_signature": False}  # In production, verify with provider's public key
)

# User info from ID token
user_email = user_claims['email']
user_name = user_claims['name']
```

## Token Exchange

```python
# Machine-to-machine authentication
response = requests.post(f"{PROVIDER_URL}/token", data={
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'scope': 'api'
})

access_token = response.json()['access_token']
```

## Best Practices

- ✅ Use PKCE for mobile/SPA
- ✅ Store refresh tokens securely
- ✅ Validate ID token signature
- ✅ Use HTTPS only
- ✅ Implement logout/revocation
- ✅ Check token expiration
- ✅ Implement state parameter
- ✅ Use short-lived tokens
