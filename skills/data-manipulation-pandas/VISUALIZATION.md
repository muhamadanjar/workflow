# Data Visualization

## Matplotlib

```python
import matplotlib.pyplot as plt

# Line plot
df.plot(x='date', y='sales')

# Scatter plot
df.plot.scatter(x='age', y='income')

# Bar chart
df['category'].value_counts().plot(kind='bar')

# Histogram
df['age'].plot(kind='hist', bins=20)

# Box plot
df.boxplot(column='age', by='category')

# Save
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
```

## Seaborn

```python
import seaborn as sns

# Scatter with regression
sns.regplot(x='age', y='income', data=df)

# Distribution
sns.histplot(df['age'], kde=True)

# Heatmap
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')

# Box plot
sns.boxplot(data=df, x='category', y='value')

# Count plot
sns.countplot(data=df, x='category')
```

## Plotly

Interactive plots:

```python
import plotly.express as px

# Scatter
fig = px.scatter(df, x='age', y='income', color='category')
fig.show()

# Bar
fig = px.bar(df, x='category', y='sales')
fig.show()

# Line
fig = px.line(df, x='date', y='value')
fig.show()
```

## Best Practices

- ✅ Choose appropriate chart type
- ✅ Label axes clearly
- ✅ Use color meaningfully
- ✅ Keep plots simple
- ✅ Save in high resolution
