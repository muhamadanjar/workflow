# GeoPandas Basics

## Installation

```bash
pip install geopandas shapely folium leaflet
```

## Geometries

### Point

Single location:

```python
from shapely.geometry import Point, LineString, Polygon
import geopandas as gpd

# Create point
p = Point(40.7128, -74.0060)  # NYC: lat, lon

# Access coordinates
p.x   # -74.0060
p.y   # 40.7128
```

### LineString

Path between points:

```python
line = LineString([(0, 0), (1, 1), (1, 0)])

# Properties
line.length
line.bounds  # (minx, miny, maxx, maxy)
```

### Polygon

Enclosed area:

```python
polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])

# Properties
polygon.area
polygon.exterior    # Boundary
polygon.interiors   # Holes
```

## GeoDataFrame

Geographic dataframe:

```python
# From list of geometries
import pandas as pd

data = {
    'name': ['NYC', 'LA', 'Chicago'],
    'geometry': [
        Point(-74.0060, 40.7128),
        Point(-118.2437, 34.0522),
        Point(-87.6298, 41.8781)
    ]
}

gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')

# From DataFrame
df = pd.DataFrame({
    'name': ['NYC', 'LA'],
    'lat': [40.7128, 34.0522],
    'lon': [-74.0060, -118.2437]
})

geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

# From shapefile
gdf = gpd.read_file('data.shp')

# From GeoJSON
gdf = gpd.read_file('data.geojson')
```

## Coordinate Reference Systems (CRS)

Location representation:

```python
# Check CRS
gdf.crs                    # EPSG:4326 (lat/lon)

# Common CRS
EPSG:4326                  # WGS84 (lat/lon) - GPS
EPSG:3857                  # Web Mercator - Web maps
EPSG:2154                  # French Lambert

# Reproject (change CRS)
gdf_projected = gdf.to_crs('EPSG:3857')

# EPSG lookup
from pyproj import CRS
crs = CRS.from_epsg(4326)
```

## Basic Operations

### Inspect

```python
gdf.head()
gdf.info()
gdf.plot()          # Simple map

# Columns
gdf.columns
gdf.geometry        # Geometry column
```

### Filter

```python
# By attribute
gdf[gdf['name'] == 'NYC']

# By geometry
gdf[gdf.geometry.area > 100]

# By bounds
gdf.cx[-75:-73, 40:41]  # Longitude, latitude
```

### Add Geometry

```python
# Buffer (create zone around geometry)
gdf['buffer'] = gdf.geometry.buffer(1000)  # 1km buffer

# Centroid
gdf['centroid'] = gdf.geometry.centroid

# Convex hull
gdf['hull'] = gdf.geometry.convex_hull
```

## Spatial Relationships

### Contains

```python
# Does polygon contain point?
polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
point = Point(0.5, 0.5)

polygon.contains(point)  # True
point.within(polygon)    # True (same thing)
```

### Intersects

```python
# Do geometries overlap?
poly1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
poly2 = Polygon([(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5)])

poly1.intersects(poly2)  # True
```

### Touches

```python
# Do geometries touch at boundary?
poly1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
poly2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])

poly1.touches(poly2)  # True (share boundary)
```

## Spatial Join

Relate geometries by location:

```python
# Points in polygon
points = gpd.GeoDataFrame(
    {'name': ['p1', 'p2', 'p3'],
     'geometry': [Point(0.5, 0.5), Point(1.5, 0.5), Point(0.2, 0.2)]}
)

polygons = gpd.GeoDataFrame(
    {'zone': ['A', 'B'],
     'geometry': [
         Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
         Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])
     ]}
)

# Join points to polygons
result = gpd.sjoin(points, polygons, how='left', predicate='within')
```

## Distance

```python
from shapely.geometry import Point

point1 = Point(0, 0)
point2 = Point(3, 4)

point1.distance(point2)  # 5.0

# Distance between GeoDataFrames
gdf['distance_to_center'] = gdf.geometry.distance(Point(0, 0))
```

## Export

```python
# Shapefile
gdf.to_file('output.shp')

# GeoJSON
gdf.to_file('output.geojson', driver='GeoJSON')

# CSV (with geometry as WKT)
gdf['geometry_wkt'] = gdf.geometry.to_wkt()
gdf.to_csv('output.csv')
```

## Common CRS Codes

```
EPSG:4326  - WGS84 (Global, lat/lon)
EPSG:3857  - Web Mercator (Web maps)
EPSG:2154  - Lambert93 (France)
EPSG:32633 - UTM Zone 33N (Europe)
EPSG:4269  - NAD83 (North America)
EPSG:3310  - California Albers (US)
```

## Plotting

```python
import matplotlib.pyplot as plt

# Simple plot
gdf.plot()

# With styling
gdf.plot(column='name', cmap='viridis', alpha=0.5)

# Multiple maps
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
gdf[gdf['name'] == 'NYC'].plot(ax=ax[0])
gdf[gdf['name'] == 'LA'].plot(ax=ax[1])

plt.show()
```

## Performance Tips

- Use spatial indexing
- Reproject to projected CRS for distance calculations
- Use appropriate file formats (Parquet, GeoJSON)
- Clip data to relevant areas
- Use buffers cautiously (can be slow)
