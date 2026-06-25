# Pandas Basics

## Series

1D labeled array:

```python
import pandas as pd
import numpy as np

# Create Series
s = pd.Series([1, 2, 3, 4], index=['a', 'b', 'c', 'd'])
# a    1
# b    2
# c    3
# d    4

# From dict
s = pd.Series({'a': 1, 'b': 2, 'c': 3})

# Access
s['a']        # 1
s[0]          # 1
s[[0, 2]]     # First and third
s['a':'c']    # Slice by label
```

## DataFrames

2D table structure:

```python
# Create DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'Chicago']
}
df = pd.DataFrame(data)

# Access columns
df['name']           # Series
df[['name', 'age']]  # Multiple columns

# Access rows
df.iloc[0]           # First row by position
df.loc[0]            # First row by label
df.iloc[0:2]         # First two rows

# Shape
df.shape             # (3, 3)
df.columns           # Index(['name', 'age', 'city'])
df.index             # RangeIndex(start=0, stop=3)
```

## Loading Data

```python
# CSV
df = pd.read_csv('data.csv')
df = pd.read_csv('data.csv', sep=';', encoding='utf-8')

# Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# JSON
df = pd.read_json('data.json')

# SQL
import sqlite3
conn = sqlite3.connect('database.db')
df = pd.read_sql('SELECT * FROM table', conn)

# Parquet (fast)
df = pd.read_parquet('data.parquet')

# Multiple files
import glob
files = glob.glob('data_*.csv')
df = pd.concat([pd.read_csv(f) for f in files])
```

## Data Types

```python
df.dtypes
# name     object
# age      int64
# city     object

# Convert types
df['age'] = df['age'].astype(float)
df['date'] = pd.to_datetime(df['date'])

# Check types
df['age'].dtype       # dtype('int64')
pd.api.types.is_numeric_dtype(df['age'])  # True
```

## Basic Operations

```python
# Arithmetic
df['age'] + 5
df['age'] * 2

# String operations
df['name'].str.upper()
df['name'].str.len()
df['name'].str.split(' ')

# Boolean indexing
df[df['age'] > 25]
df[(df['age'] > 25) & (df['city'] == 'NYC')]

# Add column
df['age_group'] = df['age'].apply(lambda x: 'young' if x < 30 else 'old')

# Rename
df = df.rename(columns={'name': 'full_name'})

# Drop
df = df.drop(columns=['city'])
df = df.drop(index=0)
```

## Inspection

```python
df.head()           # First 5 rows
df.tail()           # Last 5 rows
df.info()           # Column info
df.describe()       # Statistical summary
df.value_counts()   # Value frequency

# Missing data
df.isnull().sum()           # Missing per column
df[df.isnull().any(axis=1)] # Rows with any NaN
```

## Sorting

```python
# Sort by column
df.sort_values('age')
df.sort_values('age', ascending=False)

# Sort by multiple columns
df.sort_values(['city', 'age'])

# Sort by index
df.sort_index()
```

## Indexing

```python
# Set index
df = df.set_index('name')
df.loc['Alice']  # Access by name

# Reset index
df = df.reset_index()

# MultiIndex
df = df.set_index(['city', 'name'])
df.loc['NYC']           # All rows in NYC
df.loc[('NYC', 'Alice')] # Specific row
```

## Filtering

```python
# Single condition
df[df['age'] > 25]

# Multiple conditions
df[(df['age'] > 25) & (df['city'] == 'NYC')]
df[(df['age'] > 25) | (df['age'] < 20)]

# String matching
df[df['name'].str.contains('Alice')]

# IN operator
df[df['city'].isin(['NYC', 'LA'])]

# NOT
df[~df['city'].isin(['Chicago'])]
```

## Unique & Duplicates

```python
# Unique values
df['city'].unique()           # Array
df['city'].nunique()          # Count

# Value counts
df['city'].value_counts()
# NYC       2
# LA        1

# Duplicates
df.duplicated()               # Boolean mask
df.drop_duplicates()
df.drop_duplicates(subset=['name'])
```

## Apply Functions

```python
# Column-wise
df['age'].apply(lambda x: x * 2)
df['age'].apply(np.sqrt)

# Row-wise
df.apply(lambda row: row['age'] + len(row['name']), axis=1)

# Custom function
def categorize(age):
    if age < 30:
        return 'young'
    elif age < 60:
        return 'middle'
    else:
        return 'senior'

df['age_cat'] = df['age'].apply(categorize)
```

## Save Data

```python
# CSV
df.to_csv('output.csv', index=False)

# Excel
df.to_excel('output.xlsx', sheet_name='data')

# JSON
df.to_json('output.json')

# Parquet
df.to_parquet('output.parquet')

# SQL
df.to_sql('table_name', conn, if_exists='replace')
```

## Common Gotchas

```python
# ❌ Modifying copy vs view
df2 = df[['name', 'age']]
df2['age'] = 0  # May not affect original

# ✅ Use .copy()
df2 = df[['name', 'age']].copy()

# ❌ Chained indexing
df[df['age'] > 25]['name'] = 'X'  # Warning

# ✅ Use .loc
df.loc[df['age'] > 25, 'name'] = 'X'

# ❌ Iteration
for i, row in df.iterrows():  # SLOW
    print(row['name'])

# ✅ Use vectorized operations
df['name'].apply(...)  # FAST
```

## Performance Tips

- Use vectorized operations
- Avoid loops
- Use appropriate dtypes
- Use index efficiently
- Consider chunking for large files
