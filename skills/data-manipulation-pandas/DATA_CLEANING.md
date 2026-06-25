# Data Cleaning with Pandas

## Missing Data

### Detect

```python
# Check for NaN
df.isnull()              # Boolean mask
df.isnull().sum()        # Count per column
df.isnull().sum() / len(df) * 100  # Percentage

# Rows with any missing
df[df.isnull().any(axis=1)]

# Columns with missing
missing_cols = df.columns[df.isnull().any()]
```

### Handle

```python
# Drop missing
df = df.dropna()                    # Drop any row with NaN
df = df.dropna(subset=['name'])     # Drop if specific column NaN
df = df.dropna(thresh=2)            # Keep if at least 2 non-null

# Fill missing
df = df.fillna(0)                   # Fill with constant
df = df.fillna(df.mean())           # Fill with mean
df = df.fillna(method='ffill')      # Forward fill
df = df.fillna(method='bfill')      # Backward fill

# Fill per column
df['age'] = df['age'].fillna(df['age'].median())
df['city'] = df['city'].fillna('Unknown')

# Interpolation
df = df.interpolate()               # Linear interpolation
df['value'] = df['value'].interpolate(method='polynomial', order=2)
```

## Duplicates

### Detect

```python
# Find duplicates
df[df.duplicated()]                 # All but first occurrence
df[df.duplicated(keep=False)]       # All duplicates

# Duplicate by specific columns
df[df.duplicated(subset=['name'])]
```

### Remove

```python
# Drop duplicates
df = df.drop_duplicates()
df = df.drop_duplicates(subset=['name', 'email'], keep='first')

# Keep first, last, or mark
df = df.drop_duplicates(keep='first')    # Keep first occurrence
df = df.drop_duplicates(keep='last')     # Keep last occurrence
df = df.drop_duplicates(keep=False)      # Drop all (no duplicates remain)
```

## Outliers

### Detect

```python
# Z-score
from scipy import stats
z_scores = np.abs(stats.zscore(df['age']))
outliers = z_scores > 3
df[outliers]

# IQR
Q1 = df['age'].quantile(0.25)
Q3 = df['age'].quantile(0.75)
IQR = Q3 - Q1
outliers = (df['age'] < Q1 - 1.5*IQR) | (df['age'] > Q3 + 1.5*IQR)
df[outliers]

# Percentile-based
lower = df['age'].quantile(0.05)
upper = df['age'].quantile(0.95)
outliers = (df['age'] < lower) | (df['age'] > upper)
```

### Handle

```python
# Remove
df = df[~outliers]

# Cap (clip)
df['age'] = df['age'].clip(lower=0, upper=120)

# Log transform
df['amount'] = np.log1p(df['amount'])

# Standardize
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df['age_scaled'] = scaler.fit_transform(df[['age']])
```

## Data Type Conversion

```python
# String to numeric
df['age'] = pd.to_numeric(df['age'], errors='coerce')  # NaN on error
df['amount'] = pd.to_numeric(df['amount'], errors='ignore')

# String to datetime
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Categorical
df['city'] = df['city'].astype('category')

# Object to string
df['name'] = df['name'].astype(str)

# Downcast (save memory)
df['age'] = pd.to_numeric(df['age'], downcast='integer')
```

## String Cleaning

```python
# Strip whitespace
df['name'] = df['name'].str.strip()
df['name'] = df['name'].str.lstrip()
df['name'] = df['name'].str.rstrip()

# Case
df['city'] = df['city'].str.upper()
df['city'] = df['city'].str.lower()
df['city'] = df['city'].str.title()

# Replace
df['city'] = df['city'].str.replace('New York', 'NYC')
df['city'] = df['city'].str.replace(r'\s+', ' ', regex=True)  # Regex

# Remove
df['phone'] = df['phone'].str.replace('-', '')
df['phone'] = df['phone'].str.replace(r'\D', '', regex=True)  # Remove non-digits

# Split
df[['first', 'last']] = df['name'].str.split(' ', expand=True)
```

## Value Mapping

```python
# Map values
mapping = {'NYC': 'New York', 'LA': 'Los Angeles'}
df['city'] = df['city'].map(mapping)

# Replace
df['status'] = df['status'].replace({'active': 1, 'inactive': 0})

# Conditional
df['age_group'] = df['age'].apply(
    lambda x: 'child' if x < 13 else
              'teen' if x < 18 else
              'adult'
)
```

## Validation

```python
# Check constraints
assert df['age'].min() >= 0, "Age cannot be negative"
assert df['email'].str.contains('@').all(), "Invalid emails"

# Data quality report
def data_quality_report(df):
    return {
        'null_percent': (df.isnull().sum() / len(df) * 100).round(2),
        'duplicates': df.duplicated().sum(),
        'dtypes': df.dtypes.value_counts().to_dict()
    }

report = data_quality_report(df)
```

## Normalization

```python
# Min-Max scaling
df['age_normalized'] = (df['age'] - df['age'].min()) / (df['age'].max() - df['age'].min())

# Z-score normalization
df['age_standardized'] = (df['age'] - df['age'].mean()) / df['age'].std()

# Robust scaling (less sensitive to outliers)
Q1 = df['age'].quantile(0.25)
Q3 = df['age'].quantile(0.75)
df['age_robust'] = (df['age'] - Q1) / (Q3 - Q1)
```

## Data Profiling

```python
import pandas_profiling

# Generate report
profile = df.profile_report(title='Data Profile')
profile.to_file('report.html')

# Or use ydata-profiling
from ydata_profiling import ProfileReport
ProfileReport(df, title='Data Profile').to_file('report.html')
```

## Best Practices

- ✅ Check data immediately after loading
- ✅ Document cleaning decisions
- ✅ Keep raw data, create cleaned copy
- ✅ Handle missing data explicitly
- ✅ Validate after transformation
- ✅ Use appropriate data types
- ✅ Log dropped rows
- ✅ Create data quality tests
