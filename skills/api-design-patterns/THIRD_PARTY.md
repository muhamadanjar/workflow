# Third-Party API Integration Patterns

## HTTP Client Setup

### Python
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class ExternalAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        response = await self.client.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()
    
    async def get(self, endpoint: str, **kwargs):
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs):
        return await self.request("POST", endpoint, **kwargs)
```

### Go
```go
type APIClient struct {
    BaseURL   string
    APIKey    string
    HTTPClient *http.Client
}

func (c *APIClient) Do(ctx context.Context, method, endpoint string, 
    reqBody interface{}, respBody interface{}) error {
    
    url := fmt.Sprintf("%s/%s", c.BaseURL, endpoint)
    
    var body io.Reader
    if reqBody != nil {
        data, _ := json.Marshal(reqBody)
        body = bytes.NewReader(data)
    }
    
    req, _ := http.NewRequestWithContext(ctx, method, url, body)
    req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.APIKey))
    
    resp, err := c.HTTPClient.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    json.NewDecoder(resp.Body).Decode(respBody)
    return nil
}
```

## Error Handling

### Distinguish Error Types
```python
def handle_api_error(error: httpx.HTTPStatusError):
    status = error.response.status_code
    
    if status == 401:
        raise AuthenticationError("Invalid API key")
    elif status == 403:
        raise PermissionError("Access denied")
    elif status == 429:
        raise RateLimitError("Too many requests")
    elif status == 404:
        raise NotFoundError("Resource not found")
    elif 500 <= status < 600:
        raise ServerError(f"Service error: {status}")
    else:
        raise APIError(f"API error: {status}")
```

### Retry Strategy
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def call_external_api(client, endpoint):
    try:
        return await client.get(endpoint)
    except (ConnectionError, Timeout):
        raise  # Retry on connection errors
    except httpx.HTTPStatusError as e:
        if e.response.status_code in [429, 503]:  # Rate limit or unavailable
            raise  # Retry
        else:
            raise  # Don't retry client errors
```

## Webhook Patterns

### Receiving Webhooks
```python
import hmac
import hashlib

# Verify webhook signature
def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.post("/webhooks/stripe")
async def handle_stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers["Stripe-Signature"]
    
    if not verify_webhook_signature(body, signature, STRIPE_SECRET):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    event = json.loads(body)
    
    if event["type"] == "payment_intent.succeeded":
        handle_payment_success(event["data"]["object"])
    
    return {"status": "success"}
```

### Retrying Webhooks
```python
# Store failed webhooks
class FailedWebhook(BaseModel):
    event_id: str
    payload: dict
    attempts: int
    last_error: str
    next_retry: datetime

# Async worker to retry failed webhooks
async def retry_failed_webhooks():
    while True:
        failed = get_webhooks_due_for_retry()
        for webhook in failed:
            try:
                result = await post_webhook(webhook.event_id, webhook.payload)
                webhook.delete()
            except Exception as e:
                webhook.attempts += 1
                webhook.last_error = str(e)
                webhook.next_retry = calculate_next_retry(webhook.attempts)
                webhook.save()
        
        await asyncio.sleep(60)
```

## Rate Limiting Handling

```python
import time

class RateLimitedClient:
    def __init__(self, client, requests_per_second=10):
        self.client = client
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
    
    async def get(self, endpoint: str):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        
        self.last_request_time = time.time()
        
        try:
            return await self.client.get(endpoint)
        except RateLimitError as e:
            # Back off for the specified duration
            retry_after = int(e.retry_after or 60)
            await asyncio.sleep(retry_after)
            return await self.get(endpoint)
```

## Caching External API Responses

```python
from cachetools import TTLCache

class CachedAPIClient:
    def __init__(self, client, cache_ttl=3600):
        self.client = client
        self.cache = TTLCache(maxsize=1000, ttl=cache_ttl)
    
    async def get(self, endpoint: str, cache=True):
        if cache and endpoint in self.cache:
            return self.cache[endpoint]
        
        result = await self.client.get(endpoint)
        
        if cache:
            self.cache[endpoint] = result
        
        return result
```

## Webhook Storage & Delivery

```python
class WebhookQueue:
    async def enqueue(self, event_type: str, payload: dict):
        event = {
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow(),
            "retries": 0
        }
        await redis.lpush("webhooks:queue", json.dumps(event))
    
    async def process(self):
        while True:
            event_json = await redis.brpop("webhooks:queue", timeout=1)
            if not event_json:
                continue
            
            event = json.loads(event_json[1])
            
            try:
                await send_webhook(event)
            except Exception as e:
                event["retries"] += 1
                if event["retries"] < 5:
                    # Re-queue for retry
                    await redis.lpush("webhooks:queue", json.dumps(event))
```

## OAuth 2.0 for APIs

```python
# Using an API that requires OAuth
from authlib.httpx_client import AsyncOAuth2Client

async def get_oauth_client():
    client = AsyncOAuth2Client(
        client_id='xxx',
        client_secret='yyy',
        token_endpoint='https://api.example.com/oauth/token'
    )
    return client

async def call_protected_api():
    client = await get_oauth_client()
    data = await client.get('https://api.example.com/data')
    return data.json()
```

## Common API Integration Patterns

| Pattern | When to Use | Example |
|---------|------------|---------|
| Sync HTTP | Simple, synchronous needs | Stripe API |
| Async HTTP | High throughput, multiple calls | Bulk operations |
| Polling | No webhook support | Check status periodically |
| Webhooks | Real-time events | Payment confirmations |
| Message Queue | Decoupled, retryable | Event processing |
| Cache | Expensive API calls | User profiles |
