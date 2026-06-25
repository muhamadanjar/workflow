# Presigned URLs & Signed Requests

Allow secure temporary access without credentials.

## Presigned GET (Download)

Allow user to download without AWS credentials:

```python
def generate_presigned_get_url(client, bucket, key, expiration=3600):
    """Generate URL for downloading object"""
    
    url = client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiration
    )
    
    return url

# Usage
url = generate_presigned_get_url(client, 'bucket', 'file.pdf', expiration=3600)
# Share this URL (valid for 1 hour)
print(f"Download: {url}")
```

## Presigned PUT (Upload)

Allow user to upload directly without credentials:

```python
def generate_presigned_put_url(client, bucket, key, expiration=3600, 
                               content_type='application/octet-stream'):
    """Generate URL for uploading object"""
    
    url = client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': bucket,
            'Key': key,
            'ContentType': content_type
        },
        ExpiresIn=expiration
    )
    
    return url

# Usage
url = generate_presigned_put_url(client, 'bucket', 'upload.txt', content_type='text/plain')

# Upload with curl
# curl -X PUT -H "Content-Type: text/plain" --data-binary @file.txt "{url}"
```

## Presigned POST (Browser Upload)

HTML form for browser upload:

```python
def generate_presigned_post(client, bucket, key, expiration=3600, max_size=10*1024*1024):
    """Generate POST policy for browser upload"""
    
    response = client.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        ExpiresIn=expiration,
        Conditions=[
            {'content-length-range': [0, max_size]},
            {'bucket': bucket},
        ]
    )
    
    return response

# Usage in Flask
@app.route('/upload-form')
def upload_form():
    response = generate_presigned_post(client, 'bucket', 'file.bin')
    
    return render_template('upload.html',
        url=response['url'],
        form=response['fields']
    )
```

**upload.html:**
```html
<form action="{{ url }}" method="POST" enctype="multipart/form-data">
  {% for name, value in form.items() %}
    <input type="hidden" name="{{ name }}" value="{{ value }}">
  {% endfor %}
  
  <input type="file" name="file" required>
  <button type="submit">Upload</button>
</form>
```

## Time-Based Expiration

Different expiration for different use cases:

```python
# Short-lived (5 minutes) - for real-time downloads
download_url = generate_presigned_get_url(client, 'bucket', 'secret.pdf', expiration=300)

# Medium-lived (1 hour) - for user sessions
upload_url = generate_presigned_put_url(client, 'bucket', 'user-file.txt', expiration=3600)

# Long-lived (24 hours) - for batch processes
batch_url = generate_presigned_get_url(client, 'bucket', 'report.csv', expiration=86400)
```

## Conditional Access

Require specific headers/conditions:

```python
def generate_conditional_presigned_url(client, bucket, key, 
                                       required_etag=None, 
                                       required_range=None):
    """Generate URL with conditional access"""
    
    conditions = []
    
    if required_etag:
        conditions.append({'ETag': required_etag})
    
    if required_range:
        conditions.append({'content-length-range': required_range})
    
    params = {
        'Bucket': bucket,
        'Key': key,
        'Conditions': conditions
    } if conditions else {'Bucket': bucket, 'Key': key}
    
    return client.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
```

## Custom Headers

Add security headers to presigned URL:

```python
def generate_url_with_headers(client, bucket, key):
    """Add response headers to presigned URL"""
    
    url = client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket,
            'Key': key,
            'ResponseContentDisposition': 'attachment; filename="download.txt"',
            'ResponseContentType': 'text/plain'
        },
        ExpiresIn=3600
    )
    
    return url
```

## Expiring Downloads

Auto-delete after download:

```python
def create_temporary_download_url(client, bucket, key, lifetime_hours=24):
    """Create URL that auto-expires"""
    
    # Set object to expire
    client.put_object_tagging(
        Bucket=bucket,
        Key=key,
        Tagging={'TagSet': [
            {'Key': 'temporary', 'Value': 'true'},
            {'Key': 'expires', 'Value': str(lifetime_hours)}
        ]}
    )
    
    # Generate URL
    url = client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=lifetime_hours * 3600
    )
    
    return url
```

## Cloudfront Presigned URLs

For CDN-delivered content:

```python
import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64

def generate_cloudfront_url(distribution_url, key, private_key_path, expiration_days=1):
    """Generate CloudFront presigned URL"""
    
    # Load private key
    with open(private_key_path, 'rb') as f:
        private_key = f.read()
    
    # Create signer
    from botocore.signers import CloudFrontSigner
    
    signer = CloudFrontSigner(key_id, private_key)
    
    # Generate URL
    url = signer.generate_presigned_url(
        f"{distribution_url}/{key}",
        date_less_than=datetime.datetime.utcnow() + datetime.timedelta(days=expiration_days)
    )
    
    return url
```

## Security Considerations

```python
def generate_secure_presigned_url(client, bucket, key):
    """Secure presigned URL best practices"""
    
    # Short expiration
    url = client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=300  # 5 minutes only
    )
    
    return url

# Best practices:
# ✅ Short expiration (5-60 minutes)
# ✅ Specific keys (not wildcard)
# ✅ IP restrictions (if available)
# ✅ HTTPS only
# ✅ Log usage
# ✅ Monitor for abuse
```

## Revocation Pattern

Pre-signed URLs can't be revoked. Use workaround:

```python
class SecureUrlManager:
    def __init__(self, client, bucket):
        self.client = client
        self.bucket = bucket
        self.revoked_urls = set()
    
    def generate_url(self, key):
        url = self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=3600
        )
        return url
    
    def revoke_url(self, url):
        """Track revoked URLs in app"""
        self.revoked_urls.add(url)
    
    def is_valid(self, url):
        """Check if URL is revoked"""
        return url not in self.revoked_urls

# Usage
manager = SecureUrlManager(client, 'bucket')

# Generate URL
url = manager.generate_url('file.txt')

# Revoke it
manager.revoke_url(url)

# Check
if manager.is_valid(url):
    # Serve file
    pass
```

## Go Implementation

```go
import "github.com/aws/aws-sdk-go-v2/service/s3"

func GeneratePresignedURL(ctx context.Context, client *s3.Client, 
    bucket, key string) (string, error) {
    
    presignClient := s3.NewPresignClient(client)
    
    request, err := presignClient.PresignGetObject(ctx, &s3.GetObjectInput{
        Bucket: aws.String(bucket),
        Key:    aws.String(key),
    }, func(opts *s3.PresignOptions) {
        opts.Expires = time.Duration(time.Hour)
    })
    
    if err != nil {
        return "", err
    }
    
    return request.URL, nil
}
```

## Best Practices

- ✅ Use short expiration (5-60 minutes)
- ✅ Specific keys, not wildcards
- ✅ Log presigned URL generation
- ✅ Monitor for unusual patterns
- ✅ Use HTTPS only
- ✅ IP restrict if possible
- ✅ Implement revocation pattern
- ✅ Set appropriate content headers
