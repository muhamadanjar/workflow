# Security & Access Control

## IAM Policies

Fine-grained access control:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowListBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-bucket"
    },
    {
      "Sid": "AllowGetObject",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    },
    {
      "Sid": "AllowPutObject",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-bucket/uploads/*"
    }
  ]
}
```

## Bucket Policies

Public/conditional access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/public/*"
    },
    {
      "Sid": "DenyUnencryptedUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

## Encryption

### Server-Side Encryption (SSE)

```python
# SSE-S3
client.put_object(
    Bucket='bucket',
    Key='file.txt',
    Body=b'data',
    ServerSideEncryption='AES256'
)

# SSE-KMS
client.put_object(
    Bucket='bucket',
    Key='file.txt',
    Body=b'data',
    ServerSideEncryption='aws:kms',
    SSEKMSKeyId='arn:aws:kms:region:account:key/id'
)
```

### Client-Side Encryption

```python
from cryptography.fernet import Fernet
import base64

def encrypt_and_upload(client, bucket, key, data, encryption_key):
    """Encrypt before uploading"""
    
    cipher = Fernet(encryption_key)
    encrypted = cipher.encrypt(data)
    
    client.put_object(Bucket=bucket, Key=key, Body=encrypted)

def download_and_decrypt(client, bucket, key, encryption_key):
    """Download and decrypt"""
    
    response = client.get_object(Bucket=bucket, Key=key)
    encrypted = response['Body'].read()
    
    cipher = Fernet(encryption_key)
    decrypted = cipher.decrypt(encrypted)
    
    return decrypted

# Generate key
key = Fernet.generate_key()
```

## Access Logging

Track who accessed what:

```python
# Enable logging
client.put_bucket_logging(
    Bucket='my-bucket',
    BucketLoggingStatus={
        'LoggingEnabled': {
            'TargetBucket': 'log-bucket',
            'TargetPrefix': 's3-access-logs/'
        }
    }
)
```

## Versioning & MFA Delete

Prevent accidental deletion:

```python
# Enable versioning
client.put_bucket_versioning(
    Bucket='bucket',
    VersioningConfiguration={'Status': 'Enabled'}
)

# Enable MFA delete (requires root account)
client.put_bucket_versioning(
    Bucket='bucket',
    VersioningConfiguration={
        'Status': 'Enabled',
        'MFADelete': 'Enabled'
    },
    MFA='device-serial number-token'
)

# List versions
versions = client.list_object_versions(Bucket='bucket')
```

## Cross-Origin Resource Sharing (CORS)

Allow browser requests:

```python
client.put_bucket_cors(
    Bucket='bucket',
    CORSConfiguration={
        'CORSRules': [
            {
                'AllowedMethods': ['GET', 'PUT', 'POST'],
                'AllowedOrigins': ['https://example.com'],
                'AllowedHeaders': ['*'],
                'ExposeHeaders': ['ETag'],
                'MaxAgeSeconds': 3000
            }
        ]
    }
)
```

## Block Public Access

Prevent accidental public exposure:

```python
client.put_public_access_block(
    Bucket='bucket',
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
)
```

## Object ACL

Per-object access control:

```python
# Private (default)
client.put_object_acl(
    Bucket='bucket',
    Key='secret.txt',
    ACL='private'
)

# Public read
client.put_object_acl(
    Bucket='bucket',
    Key='public.txt',
    ACL='public-read'
)

# Authenticated users
client.put_object_acl(
    Bucket='bucket',
    Key='internal.txt',
    ACL='authenticated-read'
)
```

## Bucket Policies for Specific IPs

Restrict access by IP:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowFromOffice",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::bucket/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        }
      }
    }
  ]
}
```

## Secure Credential Management

Never hardcode credentials:

```python
# Good: Use IAM roles (EC2, Lambda)
client = boto3.client('s3')  # Auto-uses IAM role

# Good: Use environment variables
import os
access_key = os.environ['AWS_ACCESS_KEY_ID']
secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

# Good: Use credential files
# ~/.aws/credentials
client = boto3.client('s3')  # Auto-loads from credentials file

# Bad: Hardcoded
# client = boto3.client('s3', aws_access_key_id='xxx', aws_secret_access_key='yyy')
```

## SSL/TLS

Always use HTTPS:

```python
# Enforce HTTPS
bucket_policy = {
    "Statement": [{
        "Effect": "Deny",
        "Principal": "*",
        "Action": "s3:*",
        "Resource": [
            "arn:aws:s3:::bucket",
            "arn:aws:s3:::bucket/*"
        ],
        "Condition": {
            "Bool": {"aws:SecureTransport": "false"}
        }
    }]
}

client.put_bucket_policy(Bucket='bucket', Policy=json.dumps(bucket_policy))
```

## Audit & Compliance

CloudTrail logging:

```python
# Enable CloudTrail for S3
import boto3

cloudtrail = boto3.client('cloudtrail')
cloudtrail.start_logging(Name='s3-audit-trail')
```

## Bucket Encryption by Default

```python
client.put_bucket_encryption(
    Bucket='bucket',
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            }
        ]
    }
)
```

## Lifecycle Delete

Auto-delete old versions:

```python
client.put_bucket_lifecycle_configuration(
    Bucket='bucket',
    LifecycleConfiguration={
        'Rules': [
            {
                'Id': 'delete-old-versions',
                'NoncurrentVersionExpiration': {
                    'NoncurrentDays': 30  # Delete versions older than 30 days
                },
                'Status': 'Enabled'
            }
        ]
    }
)
```

## Security Checklist

- ✅ Never hardcode credentials
- ✅ Use IAM roles
- ✅ Enable encryption (SSE or client-side)
- ✅ Enable versioning
- ✅ Enable MFA delete
- ✅ Enable logging
- ✅ Block public access
- ✅ Use HTTPS only
- ✅ Set appropriate bucket policies
- ✅ Audit with CloudTrail
- ✅ Rotate access keys regularly
- ✅ Use presigned URLs with short expiration
- ✅ Enable object tagging for compliance
