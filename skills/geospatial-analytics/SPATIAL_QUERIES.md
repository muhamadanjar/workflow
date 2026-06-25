# Spatial Queries and Operations

## Spatial Relationships

### Predicate Functions

```python
import geopandas as gpd
from shapely.geometry import Point, Polygon

# Within (point in polygon)
result = gdf[gdf.geometry.within(polygon)]

# Contains (polygon contains point)
result = gdf[gdf.geometry.contains(point)]

# Intersects (geometries overlap)
result = gdf[gdf.geometry.intersects(polygon)]

# Touches (share boundary)
result = gdf[gdf.geometry.touches(polygon)]

# Crosses (geometries cross)
result = gdf[gdf.geometry.crosses(line)]

# Equals (same geometry)
result = gdf[gdf.geometry.equals(polygon)]

# Disjoint (no overlap)
result = gdf[gdf.geometry.disjoint(polygon)]
```

## Spatial Joins

Combine GeoDataFrames based on location:

```python
# Points within polygons
points = gpd.GeoDataFrame(...)  # Point geometries
zones = gpd.GeoDataFrame(...)   # Polygon geometries

result = gpd.sjoin(points, zones, how='left', predicate='within')
# Result: points with zone attribute

# Nearest neighbor
result = gpd.sjoin_nearest(points, zones, how='left')
# Points matched to nearest zone
```

## Buffer Operations

Create zones around geometries:

```python
# Simple buffer
gdf['buffer'] = gdf.geometry.buffer(1000)  # 1000 meters

# With cap style
buffered = gdf.geometry.buffer(100, cap_style='round')

# Negative buffer (shrink)
buffered = gdf.geometry.buffer(-100)

# For analysis
result = gpd.GeoDataFrame(geometry=gdf['buffer'])
```

## Geometric Operations

### Union

Combine geometries:

```python
# Union of all geometries
combined = gdf.geometry.unary_union

# Union of two
union = geom1.union(geom2)
```

### Intersection

Find overlap:

```python
# Intersection of geometries
intersection = gdf.geometry.intersection(polygon)

# Non-empty intersections
result = gdf[~gdf.geometry.intersection(polygon).is_empty]
```

### Difference

Remove area:

```python
# Subtract polygon from all geometries
difference = gdf.geometry.difference(polygon)
```

### Symmetric Difference

Non-overlapping areas:

```python
# Parts of either but not both
sym_diff = gdf.geometry.symmetric_difference(polygon)
```

## Distance Calculations

```python
# Distance to point
center = Point(0, 0)
gdf['distance'] = gdf.geometry.distance(center)

# Distance between rows
distances = gdf.geometry.distance(gdf.geometry.shift())

# Nearest distance to other GeoDataFrame
gdf['nearest_dist'] = gdf.geometry.distance(other_gdf.geometry.unary_union)

# Distance matrix
from scipy.spatial.distance import pdist, squareform
coords = list(gdf.geometry.apply(lambda g: (g.x, g.y)))
dist_matrix = squareform(pdist(coords))
```

## Nearest Neighbor

Find closest features:

```python
# Nearest neighbor join
result = gpd.sjoin_nearest(gdf1, gdf2, how='left')

# Custom function
def nearest_feature(row, gdf):
    return gdf.geometry.distance(row.geometry).idxmin()

gdf['nearest'] = gdf.apply(nearest_feature, gdf=other_gdf, axis=1)
```

## Clustering

Group nearby geometries:

```python
from sklearn.cluster import DBSCAN
import numpy as np

# Coordinates
coords = np.column_stack([gdf.geometry.x, gdf.geometry.y])

# DBSCAN clustering
clustering = DBSCAN(eps=0.05, min_samples=2).fit(coords)
gdf['cluster'] = clustering.labels_

# Convex hull per cluster
gdf.groupby('cluster').apply(lambda x: x.geometry.unary_union.convex_hull)
```

## Reverse Geocoding

Address from coordinates:

```python
from geopy.geocoders import Nominatim

gelocator = Nominatim(user_agent='my-app')

def reverse_geocode(row):
    return gelocator.reverse(f"{row.geometry.y}, {row.geometry.x}").address

gdf['address'] = gdf.apply(reverse_geocode, axis=1)
```

## Geocoding

Coordinates from address:

```python
from geopy.geocoders import Nominatim

geocoder = Nominatim(user_agent='my-app')

def geocode_address(address):
    location = geocoder.geocode(address)
    return Point(location.longitude, location.latitude)

gdf['geometry'] = gdf['address'].apply(geocode_address)
```

## Spatial Aggregation

Aggregate data by location:

```python
# Count points in each polygon
counts = gpd.sjoin(points, zones, how='left').groupby('zone').size()

# Sum values in zones
totals = gpd.sjoin(points, zones, how='left').groupby('zone')['value'].sum()

# Spatial dissolve (merge by attribute)
dissolved = gdf.dissolve(by='zone', aggfunc='sum')
```

## Performance Optimization

```python
# Spatial index (automatic with GeoDataFrame)
sindex = gdf.spatial_index

# Use spatial index for quick filtering
possible_matches = list(sindex.intersection(geom.bounds))

# Clip to region
clipped = gpd.clip(gdf, mask)

# Simplify geometries (reduce vertices)
gdf['geometry'] = gdf.geometry.simplify(tolerance=0.01)
```

## Best Practices

- ✅ Use projected CRS for distance calculations
- ✅ Leverage spatial indexing
- ✅ Simplify complex geometries
- ✅ Cache spatial joins
- ✅ Test with small datasets first
- ✅ Monitor memory usage
- ✅ Use appropriate predicates
