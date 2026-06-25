# Performance Optimization

## Transfer Acceleration

Faster uploads via edge locations:

```python
# Enable transfer acceleration on bucket
client.put_bucket_accelerate_configuration(
    Bucket='bucket',
    AccelerateConfiguration={'Status': 'Enabled'}
)

# Use accelerated endpoint
client = boto3.client('s3',
    endpoint_url='https://bucket.s3-accelerate.amazonaws.com'
)
```

## Multipart Thresholds

Tune for your use case:

```python
import boto3
from botocore.config import Config

# Configure for large files
config = Config(
    s3={'max_concurrent_requests': 20},
    max_pool_connections=50
)

client = boto3.client('s3', config=config)

# Multipart threshold (default 8MB)
client = boto3.client('s3',
    config=Config(
        s3={'payload_signing_enabled': False}
    )
)
```

## Connection Pooling

Reuse connections:

```python
# Use single client for all operations
client = boto3.client('s3')

# Reuse across requests
for file in files:
    client.upload_file(file, 'bucket', f'uploads/{file}')

# Don't create new client per request!
```

## Caching Strategy

Cache frequently accessed objects:

```python
class CachedS3Client:
    def __init__(self, client, cache_dir='./s3_cache'):
        self.client = client
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_object(self, bucket, key):
        # Check cache
        cache_path = os.path.join(self.cache_dir, key.replace('/', '_'))
        
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                return f.read()
        
        # Download
        response = self.client.get_object(Bucket=bucket, Key=key)
        data = response['Body'].read()
        
        # Cache
        with open(cache_path, 'wb') as f:
            f.write(data)
        
        return data

# Usage
cache = CachedS3Client(client)
data = cache.get_object('bucket', 'common-file.txt')
```

## Batch Operations

Process multiple files efficiently:

```python
def batch_upload(client, bucket, files, prefix='', max_workers=5):
    """Upload multiple files concurrently"""
    
    from concurrent.futures import ThreadPoolExecutor
    
    def upload_file(local_file):
        s3_key = f"{prefix}{os.path.basename(local_file)}"
        client.upload_file(local_file, bucket, s3_key)
        return s3_key
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        keys = list(executor.map(upload_file, files))
    
    return keys

def batch_download(client, bucket, keys, dest_dir, max_workers=5):
    """Download multiple files concurrently"""
    
    from concurrent.futures import ThreadPoolExecutor
    
    def download_file(key):
        dest = os.path.join(dest_dir, os.path.basename(key))
        client.download_file(bucket, key, dest)
        return dest
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        paths = list(executor.map(download_file, keys))
    
    return paths
```

## Compression

Reduce transfer size:

```python
import gzip
import io

def upload_compressed(client, bucket, data, key):
    """Upload compressed data"""
    
    # Compress
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode='wb') as gz:
        gz.write(data)
    
    # Upload
    compressed.seek(0)
    client.upload_fileobj(
        compressed,
        bucket,
        f"{key}.gz",
        ExtraArgs={'ContentEncoding': 'gzip'}
    )

def download_compressed(client, bucket, key):
    """Download and decompress"""
    
    # Download
    response = client.get_object(Bucket=bucket, Key=key)
    
    # Decompress
    with gzip.GzipFile(fileobj=response['Body']) as gz:
        data = gz.read()
    
    return data
```

## Request Optimization

Minimize API calls:

```python
# Bad: Multiple list calls
for prefix in ['a/', 'b/', 'c/']:
    response = client.list_objects_v2(Bucket='bucket', Prefix=prefix)

# Good: Single call with pagination
paginator = client.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket='bucket', PaginationConfig={'MaxItems': 10000})

all_objects = []
for page in pages:
    all_objects.extend(page.get('Contents', []))
```

## Bandwidth Throttling

Rate limit uploads/downloads:

```python
import time
from threading import Semaphore

class ThrottledS3Client:
    def __init__(self, client, bps_limit=1*1024*1024):  # 1 MB/s
        self.client = client
        self.bps_limit = bps_limit
        self.last_time = time.time()
        self.bytes_sent = 0
    
    def upload_file(self, local_file, bucket, key):
        file_size = os.path.getsize(local_file)
        
        with open(local_file, 'rb') as f:
            def throttle_callback(bytes_amount):
                elapsed = time.time() - self.last_time
                expected_time = self.bytes_sent / self.bps_limit
                
                if elapsed < expected_time:
                    time.sleep(expected_time - elapsed)
                
                self.bytes_sent += bytes_amount
            
            self.client.upload_fileobj(
                f, bucket, key,
                Callback=throttle_callback
            )
```

## Memory Efficiency

Stream large files:

```python
def process_large_file(client, bucket, key, process_func, chunk_size=1024*1024):
    """Process large file without loading in memory"""
    
    response = client.get_object(Bucket=bucket, Key=key)
    
    with response['Body'] as stream:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            process_func(chunk)
```

## CDN Integration

Cache with CloudFront:

```python
# Enable CloudFront caching
client.put_bucket_cors(
    Bucket='bucket',
    CORSConfiguration={
        'CORSRules': [{
            'AllowedMethods': ['GET', 'HEAD'],
            'AllowedOrigins': ['*'],
            'MaxAgeSeconds': 3600
        }]
    }
)

# CloudFront will cache GET requests
# Set Cache-Control headers
client.put_object(
    Bucket='bucket',
    Key='static.css',
    Body=data,
    CacheControl='max-age=31536000'  # 1 year for immutable content
)
```

## Metrics & Monitoring

Track performance:

```python
import time

class MonitoredS3Client:
    def __init__(self, client):
        self.client = client
        self.metrics = {
            'uploads': 0,
            'downloads': 0,
            'total_time': 0,
            'total_bytes': 0
        }
    
    def upload_file(self, local_file, bucket, key):
        start = time.time()
        file_size = os.path.getsize(local_file)
        
        self.client.upload_file(local_file, bucket, key)
        
        elapsed = time.time() - start
        self.metrics['uploads'] += 1
        self.metrics['total_time'] += elapsed
        self.metrics['total_bytes'] += file_size
    
    def get_metrics(self):
        if self.metrics['uploads'] == 0:
            return {}
        
        return {
            'avg_upload_time': self.metrics['total_time'] / self.metrics['uploads'],
            'throughput_mbps': (self.metrics['total_bytes'] / (1024*1024)) / self.metrics['total_time']
        }

# Usage
monitor = MonitoredS3Client(client)
monitor.upload_file('file.bin', 'bucket', 'file.bin')
print(monitor.get_metrics())
```

## Best Practices

- ✅ Reuse S3 client connections
- ✅ Use multipart for large files
- ✅ Implement connection pooling
- ✅ Batch operations
- ✅ Compress before upload
- ✅ Stream large files
- ✅ Use CDN (CloudFront)
- ✅ Monitor metrics
- ✅ Set appropriate cache headers
- ✅ Implement rate limiting
