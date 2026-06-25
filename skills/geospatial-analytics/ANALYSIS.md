# Spatial Analysis

## Proximity Analysis

```python
import geopandas as gpd
from shapely.geometry import Point

# Nearest neighbor
nearest = gpd.sjoin_nearest(points, zones)

# Distance
gdf['distance_to_center'] = gdf.geometry.distance(Point(0, 0))

# Nearest point from another GeoDataFrame
for idx, row in gdf.iterrows():
    nearest = other_gdf.geometry.distance(row.geometry).idxmin()
    gdf.loc[idx, 'nearest_name'] = other_gdf.loc[nearest, 'name']
```

## Clustering

```python
from sklearn.cluster import DBSCAN
import numpy as np

# Get coordinates
coords = np.column_stack([gdf.geometry.x, gdf.geometry.y])

# DBSCAN
clustering = DBSCAN(eps=0.05, min_samples=2).fit(coords)
gdf['cluster'] = clustering.labels_

# Cluster bounds
for cluster_id in gdf['cluster'].unique():
    cluster_gdf = gdf[gdf['cluster'] == cluster_id]
    bounds = cluster_gdf.geometry.unary_union.bounds
```

## Hotspot Analysis

```python
# Kernel Density Estimation
from scipy.stats import gaussian_kde

coords = np.column_stack([gdf.geometry.x, gdf.geometry.y])
kde = gaussian_kde(coords.T)

# Density at grid
x, y = np.meshgrid(np.linspace(minx, maxx, 100), np.linspace(miny, maxy, 100))
positions = np.vstack([x.ravel(), y.ravel()])
density = kde(positions).reshape(x.shape)
```

## Area Analysis

```python
# Calculate area
gdf['area'] = gdf.geometry.area

# Find largest
largest = gdf.loc[gdf['area'].idxmax()]

# Percentage of total
gdf['percent'] = (gdf['area'] / gdf['area'].sum()) * 100
```

## Overlay Operations

```python
# Spatial intersection
result = gpd.overlay(gdf1, gdf2, how='intersection')

# Union
result = gpd.overlay(gdf1, gdf2, how='union')

# Difference
result = gpd.overlay(gdf1, gdf2, how='difference')
```

## Best Practices

- ✅ Use projected CRS for analysis
- ✅ Validate geometry
- ✅ Handle edge cases
- ✅ Document assumptions
