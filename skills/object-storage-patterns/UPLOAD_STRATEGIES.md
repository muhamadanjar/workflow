# Upload Strategies

## Simple Upload

Best for: Small files (<100MB)

```python
def upload_file(client, bucket, local_path, s3_key):
    client.upload_file(local_path, bucket, s3_key)
    print(f"Uploaded: {s3_key}")
```

## Streaming Upload

Best for: Large files, memory constrained

```python
import io

def upload_stream(client, bucket, file_obj, s3_key):
    client.upload_fileobj(file_obj, bucket, s3_key)

# From file
with open('large_file.bin', 'rb') as f:
    upload_stream(client, 'bucket', f, 'large_file.bin')

# From bytes
data = io.BytesIO(b'file content')
upload_stream(client, 'bucket', data, 'file.txt')
```

## Multipart Upload

Best for: Large files (>100MB), resume capability

```python
def multipart_upload(client, bucket, local_file, s3_key, part_size=5*1024*1024):
    """Upload large file in parts"""
    
    # Initiate
    response = client.create_multipart_upload(Bucket=bucket, Key=s3_key)
    upload_id = response['UploadId']
    
    parts = []
    
    try:
        with open(local_file, 'rb') as f:
            part_num = 1
            
            while True:
                data = f.read(part_size)
                if not data:
                    break
                
                # Upload part
                part_response = client.upload_part(
                    Bucket=bucket,
                    Key=s3_key,
                    PartNumber=part_num,
                    UploadId=upload_id,
                    Body=data
                )
                
                parts.append({
                    'ETag': part_response['ETag'],
                    'PartNumber': part_num
                })
                
                print(f"Uploaded part {part_num}")
                part_num += 1
        
        # Complete
        client.complete_multipart_upload(
            Bucket=bucket,
            Key=s3_key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        print("Upload complete")
        
    except Exception as e:
        # Abort on error
        client.abort_multipart_upload(
            Bucket=bucket,
            Key=s3_key,
            UploadId=upload_id
        )
        raise e
```

## Resumable Upload

Handle interruptions:

```python
def resumable_upload(client, bucket, local_file, s3_key):
    """Resume interrupted uploads"""
    
    file_size = os.path.getsize(local_file)
    part_size = 10 * 1024 * 1024  # 10MB parts
    
    # Check existing uploads
    response = client.list_multipart_uploads(Bucket=bucket)
    
    upload_id = None
    parts = []
    
    for upload in response.get('Uploads', []):
        if upload['Key'] == s3_key:
            upload_id = upload['UploadId']
            
            # List completed parts
            parts_response = client.list_parts(
                Bucket=bucket,
                Key=s3_key,
                UploadId=upload_id
            )
            
            parts = parts_response.get('Parts', [])
            break
    
    # If no existing upload, create new
    if not upload_id:
        response = client.create_multipart_upload(Bucket=bucket, Key=s3_key)
        upload_id = response['UploadId']
    
    # Upload remaining parts
    completed_parts = {p['PartNumber'] for p in parts}
    
    with open(local_file, 'rb') as f:
        part_num = 1
        
        while True:
            if part_num in completed_parts:
                f.seek((part_num - 1) * part_size)
                part_num += 1
                continue
            
            data = f.read(part_size)
            if not data:
                break
            
            part_response = client.upload_part(
                Bucket=bucket,
                Key=s3_key,
                PartNumber=part_num,
                UploadId=upload_id,
                Body=data
            )
            
            parts.append({
                'ETag': part_response['ETag'],
                'PartNumber': part_num
            })
            
            print(f"Uploaded part {part_num}")
            part_num += 1
    
    # Complete
    client.complete_multipart_upload(
        Bucket=bucket,
        Key=s3_key,
        UploadId=upload_id,
        MultipartUpload={'Parts': sorted(parts, key=lambda x: x['PartNumber'])}
    )
```

## Direct Browser Upload

Presigned POST:

```python
def generate_presigned_post(client, bucket, key, expiration=3600):
    """Generate POST policy for browser upload"""
    
    response = client.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        ExpiresIn=expiration,
        Conditions=[
            {'content-length-range': [0, 10*1024*1024]},  # Max 10MB
        ]
    )
    
    return response
```

**HTML Form:**
```html
<form action="{{ url }}" method="POST" enctype="multipart/form-data">
  {% for name, value in form.items() %}
    <input type="hidden" name="{{ name }}" value="{{ value }}">
  {% endfor %}
  
  <input type="file" name="file">
  <button type="submit">Upload</button>
</form>
```

## Progress Tracking

```python
def upload_with_progress(client, bucket, local_file, s3_key):
    """Track upload progress"""
    
    file_size = os.path.getsize(local_file)
    
    def progress_callback(bytes_transferred):
        percent = (bytes_transferred / file_size) * 100
        print(f"Progress: {percent:.1f}%")
    
    # Use callback
    client.upload_file(
        local_file,
        bucket,
        s3_key,
        Callback=progress_callback
    )
```

## Concurrent Uploads

Multiple parts simultaneously:

```python
from concurrent.futures import ThreadPoolExecutor

def concurrent_multipart_upload(client, bucket, local_file, s3_key, max_workers=4):
    """Upload parts concurrently"""
    
    file_size = os.path.getsize(local_file)
    part_size = 10 * 1024 * 1024
    
    # Initiate
    response = client.create_multipart_upload(Bucket=bucket, Key=s3_key)
    upload_id = response['UploadId']
    
    parts = []
    
    def upload_part(part_num):
        with open(local_file, 'rb') as f:
            f.seek((part_num - 1) * part_size)
            data = f.read(part_size)
            
            response = client.upload_part(
                Bucket=bucket,
                Key=s3_key,
                PartNumber=part_num,
                UploadId=upload_id,
                Body=data
            )
            
            return {
                'PartNumber': part_num,
                'ETag': response['ETag']
            }
    
    # Calculate part count
    part_count = (file_size + part_size - 1) // part_size
    
    # Upload concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(upload_part, i)
            for i in range(1, part_count + 1)
        ]
        
        for future in futures:
            parts.append(future.result())
    
    # Complete
    client.complete_multipart_upload(
        Bucket=bucket,
        Key=s3_key,
        UploadId=upload_id,
        MultipartUpload={'Parts': sorted(parts, key=lambda x: x['PartNumber'])}
    )
```

## Error Handling

```python
def robust_upload(client, bucket, local_file, s3_key, max_retries=3):
    """Upload with retry logic"""
    
    import time
    
    for attempt in range(max_retries):
        try:
            client.upload_file(local_file, bucket, s3_key)
            print("Upload successful")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'NoSuchBucket':
                print("Bucket does not exist")
                return False
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry after {wait_time}s")
                time.sleep(wait_time)
            else:
                print("Max retries reached")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False
```

## Best Practices

- ✅ Use multipart for files >100MB
- ✅ Enable resumable upload for large files
- ✅ Track progress for UX
- ✅ Handle errors gracefully
- ✅ Validate file before upload
- ✅ Set appropriate timeouts
- ✅ Monitor bandwidth
- ✅ Clean up on errors
