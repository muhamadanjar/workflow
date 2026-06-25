# Statistical Analysis

## Descriptive Statistics

```python
# Summary stats
df.describe()
df.describe(include='all')  # Include object columns

# Specific statistics
df['age'].mean()
df['age'].median()
df['age'].std()
df['age'].var()
df['age'].min()
df['age'].max()
df['age'].quantile([0.25, 0.5, 0.75])
```

## Correlation

```python
# Correlation matrix
corr = df.corr()

# Specific correlation
df['age'].corr(df['income'])

# Heatmap
import seaborn as sns
sns.heatmap(df.corr(), annot=True)
```

## Time Series

```python
# Set datetime index
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')

# Resample
df.resample('M').mean()  # Monthly average
df.resample('D').sum()   # Daily sum

# Rolling window
df.rolling(window=7).mean()

# Lag
df['lag1'] = df.shift(1)

# Difference
df['diff'] = df.diff()
```

## Distributions

```python
# Value distribution
df['age'].value_counts()
df['age'].value_counts(normalize=True)  # Proportions

# Histogram
df['age'].hist(bins=20)

# Unique values
df['category'].nunique()
```

## Grouping & Aggregation

```python
# Multiple aggregations
grouped = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'std'],
    'quantity': 'count'
})

# Custom function
result = df.groupby('category').agg(lambda x: x.max() - x.min())

# Transform
df['normalized'] = df.groupby('category')['sales'].transform(lambda x: (x - x.mean()) / x.std())
```

## Hypothesis Testing

```python
from scipy import stats

# T-test
t_stat, p_value = stats.ttest_ind(group1, group2)

# Chi-square
chi2, p_value = stats.chisquare(df['category'].value_counts())

# Correlation test
corr, p_value = stats.pearsonr(df['x'], df['y'])
```

## Best Practices

- ✅ Check data types before analysis
- ✅ Handle missing values appropriately
- ✅ Use groupby for subgroup analysis
- ✅ Validate outliers
- ✅ Document findings
