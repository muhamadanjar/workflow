# Performance & Optimization

## Spatial Indexing

```python
# Built-in spatial index
sindex = gdf.spatial_index

# Query by bounds
bounds = geometry.bounds  # (minx, miny, maxx, maxy)
candidates = list(sindex.intersection(bounds))

# Use in operations
result = gdf.iloc[candidates]
```

## Geometry Simplification

```python
# Simplify geometries
gdf['geometry'] = gdf.geometry.simplify(tolerance=0.01)

# Reduce precision
gdf['geometry'] = gdf.geometry.apply(lambda g: round_coords(g, 2))

def round_coords(geom, decimals):
    return type(geom)([round(c, decimals) for c in geom.coords])
```

## Clipping

```python
# Clip to region
clipped = gpd.clip(gdf, mask)

# Intersect
intersection = gpd.overlay(gdf, mask, how='intersection')
```

## Large Dataset Handling

```python
# Spatial join with chunking
results = []
for chunk in chunks:
    chunk_result = gpd.sjoin(chunk, zones)
    results.append(chunk_result)

result = pd.concat(results)

# Use Parquet
gdf.to_parquet('data.parquet')
gdf = gpd.read_parquet('data.parquet')
```

## Memory Optimization

```python
# Check usage
gdf.memory_usage(deep=True).sum()

# Drop unnecessary columns
gdf = gdf.drop(columns=['temp_col'])

# Convert to appropriate types
gdf['code'] = gdf['code'].astype('category')
```

## Best Practices

- ✅ Use spatial index
- ✅ Simplify geometries
- ✅ Clip to relevant area
- ✅ Use efficient formats
- ✅ Monitor memory
