# Object Storage Fundamentals

## S3 vs Minio vs Others

| Feature | AWS S3 | Minio | Google Cloud | Azure |
|---------|--------|-------|--------------|-------|
| API | S3 (standard) | S3-compatible | Cloud Storage | Blob Storage |
| Hosting | Cloud | Self-hosted | Cloud | Cloud |
| Cost | Pay-as-go | One-time | Pay-as-go | Pay-as-go |
| Use | Production | Dev/small | Enterprise | Enterprise |

## Core Concepts

### Bucket
Container for objects. Like folder.
```python
# Create bucket
client.create_bucket(Bucket='my-bucket')

# List buckets
buckets = client.list_buckets()
```

### Object
File stored in bucket. Has key (path).
```python
# Upload object
client.put_object(
    Bucket='my-bucket',
    Key='folder/file.txt',
    Body=b'content'
)

# Download object
response = client.get_object(Bucket='my-bucket', Key='folder/file.txt')
```

### Key (Path)
Unique identifier in bucket.
```
s3://bucket-name/path/to/object.txt
                 ^^^^^^^^^^^^^^^^^
                 This is the key
```

## Setup

### Python - boto3

```python
import boto3
from botocore.exceptions import ClientError

# AWS S3
s3_client = boto3.client('s3',
    aws_access_key_id='xxx',
    aws_secret_access_key='yyy',
    region_name='us-east-1'
)

# Minio
minio_client = boto3.client('s3',
    access_key='minioadmin',
    secret_key='minioadmin',
    endpoint_url='http://localhost:9000',
    region_name='us-east-1'
)
```

### Go - aws-sdk-go-v2

```go
import "github.com/aws/aws-sdk-go-v2/service/s3"

// AWS S3
cfg, _ := config.LoadDefaultConfig(context.TODO())
s3Client := s3.NewFromConfig(cfg)

// Minio
cfg, _ := config.LoadDefaultConfig(context.TODO(),
    config.WithBaseEndpoint("http://localhost:9000"),
    config.WithRegion("us-east-1"),
)
s3Client := s3.NewFromConfig(cfg)
```

### Node.js - AWS SDK v3

```javascript
import { S3Client, ListBucketsCommand } from "@aws-sdk/client-s3";

// AWS S3
const s3Client = new S3Client({ region: "us-east-1" });

// Minio
const s3Client = new S3Client({
    endpoint: "http://localhost:9000",
    region: "us-east-1",
    credentials: {
        accessKeyId: "minioadmin",
        secretAccessKey: "minioadmin"
    }
});
```

## Basic Operations

### List Buckets
```python
def list_buckets(client):
    response = client.list_buckets()
    for bucket in response['Buckets']:
        print(f"Bucket: {bucket['Name']}")
```

### Create Bucket
```python
def create_bucket(client, bucket_name, region='us-east-1'):
    try:
        if region == 'us-east-1':
            client.create_bucket(Bucket=bucket_name)
        else:
            client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Created bucket: {bucket_name}")
    except ClientError as e:
        print(f"Error: {e}")
```

### Upload Object
```python
def upload_file(client, bucket, local_file, s3_key):
    try:
        client.upload_file(local_file, bucket, s3_key)
        print(f"Uploaded {local_file} to s3://{bucket}/{s3_key}")
    except Exception as e:
        print(f"Error: {e}")
```

### Download Object
```python
def download_file(client, bucket, s3_key, local_file):
    try:
        client.download_file(bucket, s3_key, local_file)
        print(f"Downloaded s3://{bucket}/{s3_key} to {local_file}")
    except Exception as e:
        print(f"Error: {e}")
```

### List Objects
```python
def list_objects(client, bucket, prefix=''):
    response = client.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix,
        MaxKeys=1000
    )
    
    if 'Contents' not in response:
        return []
    
    return [obj['Key'] for obj in response['Contents']]
```

### Delete Object
```python
def delete_object(client, bucket, key):
    client.delete_object(Bucket=bucket, Key=key)
    print(f"Deleted s3://{bucket}/{key}")
```

## Error Handling

```python
from botocore.exceptions import ClientError

def handle_s3_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'NoSuchBucket':
                print("Bucket does not exist")
            elif error_code == 'NoSuchKey':
                print("Object does not exist")
            elif error_code == 'AccessDenied':
                print("Access denied")
            else:
                print(f"Error: {error_code}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    return wrapper
```

## Storage Classes

Different cost/performance tiers:

```python
# Standard (frequent access)
client.put_object(
    Bucket='bucket',
    Key='file.txt',
    Body=b'data',
    StorageClass='STANDARD'
)

# Infrequent access (cheaper, slower)
client.put_object(
    Bucket='bucket',
    Key='archive.zip',
    Body=data,
    StorageClass='STANDARD_IA'  # 30-day minimum
)

# Glacier (archival, very cheap)
client.put_object(
    Bucket='bucket',
    Key='backup.tar',
    Body=data,
    StorageClass='GLACIER'  # Retrieval takes hours
)
```

## Bucket Policies

Control access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

## Best Practices

- ✅ Use IAM roles (not hardcoded credentials)
- ✅ Enable versioning
- ✅ Enable MFA delete
- ✅ Use encryption
- ✅ Enable logging
- ✅ Set lifecycle policies
- ✅ Use appropriate storage class
- ✅ Monitor costs

## Pricing Model

**AWS S3 (us-east-1)**
- Storage: $0.023/GB/month (standard)
- Upload: Free
- Download: $0.09/GB (after 100GB free)
- Requests: $0.0004-0.005 per 1000 requests

**Minio (Self-hosted)**
- Initial cost: Hardware + setup
- No per-request fees
- No egress charges
