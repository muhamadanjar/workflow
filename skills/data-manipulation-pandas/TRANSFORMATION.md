# Data Transformation

## Reshape Data

### Pivot

Wide format:

```python
# Pivot table
pivot = df.pivot_table(
    values='sales',
    index='month',
    columns='product',
    aggfunc='sum'
)

# Simple pivot
pivot = df.pivot(index='date', columns='product', values='sales')
```

### Melt

Long format:

```python
# From wide to long
melted = df.melt(id_vars=['date'], var_name='product', value_name='sales')
```

## Groupby Operations

```python
# Simple groupby
groups = df.groupby('category')['sales'].sum()

# Multiple columns
groups = df.groupby(['category', 'region'])['sales'].agg(['sum', 'mean', 'count'])

# Custom aggregation
agg_dict = {
    'sales': ['sum', 'mean'],
    'quantity': 'count',
    'price': 'max'
}
result = df.groupby('category').agg(agg_dict)

# Apply function
result = df.groupby('category').apply(lambda x: x.nlargest(3, 'sales'))
```

## Merging

```python
# Inner join
merged = pd.merge(df1, df2, on='key', how='inner')

# Left join
merged = pd.merge(df1, df2, on='key', how='left')

# Outer join
merged = pd.merge(df1, df2, on='key', how='outer')

# Multiple keys
merged = pd.merge(df1, df2, on=['key1', 'key2'], how='inner')

# Suffix for duplicate columns
merged = pd.merge(df1, df2, on='key', how='left', suffixes=('_x', '_y'))
```

## Concatenation

```python
# Vertical concat
result = pd.concat([df1, df2], ignore_index=True)

# Horizontal concat
result = pd.concat([df1, df2], axis=1)

# With keys
result = pd.concat([df1, df2], keys=['first', 'second'])
```

## Stack/Unstack

```python
# Stack (wide to long)
stacked = df.stack()

# Unstack (long to wide)
unstacked = df.unstack()

# Level specification
stacked = df.stack(level=1)
```

## Explode

Expand arrays to rows:

```python
# Expand list in column
df['values'] = df['values'].apply(lambda x: [1, 2, 3])
exploded = df.explode('values')
```

## Window Functions

```python
# Rolling average
df['MA'] = df['price'].rolling(window=7).mean()

# Cumulative sum
df['cumsum'] = df['sales'].cumsum()

# Rank
df['rank'] = df['sales'].rank(method='dense')

# Percentage change
df['pct_change'] = df['price'].pct_change()
```

## Type Conversions

```python
# String to numeric
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# String to datetime
df['date'] = pd.to_datetime(df['date'])

# Categorical
df['category'] = df['category'].astype('category')
```

## Best Practices

- ✅ Use appropriate methods (pivot vs melt)
- ✅ Chain operations efficiently
- ✅ Use groupby over loops
- ✅ Specify join keys clearly
- ✅ Handle duplicates
