# Performance Optimization

## Memory Usage

```python
# Check memory
df.memory_usage(deep=True).sum()

# Reduce dtypes
df['age'] = df['age'].astype('int8')
df['name'] = df['name'].astype('category')

# Chunking
for chunk in pd.read_csv('large.csv', chunksize=10000):
    process(chunk)
```

## Speed

```python
# Vectorized operations (fast)
df['new'] = df['col1'] + df['col2']

# Loops (slow)
for i, row in df.iterrows():
    df.loc[i, 'new'] = row['col1'] + row['col2']

# Use apply
df['new'] = df.apply(lambda row: process(row), axis=1)

# Caching
df_cached = df.copy()  # If reusing
```

## Large Files

```python
# Read in chunks
reader = pd.read_csv('large.csv', chunksize=50000)

# Process
for chunk in reader:
    process(chunk)

# Parquet (faster)
df.to_parquet('data.parquet')
df = pd.read_parquet('data.parquet')
```

## Best Practices

- ✅ Use vectorized operations
- ✅ Appropriate data types
- ✅ Chunk large files
- ✅ Use efficient formats
- ✅ Profile before optimizing
