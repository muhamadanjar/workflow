# Web Integration

## REST API Endpoints

```python
from flask import Flask, jsonify
import geopandas as gpd

app = Flask(__name__)
gdf = gpd.read_file('data.geojson')

# Get all features
@app.route('/api/features')
def get_features():
    return gdf.to_geo_json()

# Get by location
@app.route('/api/features/<lat>/<lon>')
def get_nearby(lat, lon):
    from shapely.geometry import Point
    point = Point(float(lon), float(lat))
    nearby = gdf[gdf.geometry.distance(point) < 1.0]
    return nearby.to_geo_json()

# Spatial query
@app.route('/api/contains/<lat>/<lon>')
def contains_point(lat, lon):
    from shapely.geometry import Point
    point = Point(float(lon), float(lat))
    result = gdf[gdf.geometry.contains(point)]
    return result.to_geo_json()
```

## GeoJSON Format

```python
# Export GeoJSON
gdf.to_file('data.geojson', driver='GeoJSON')

# GeoJSON structure
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "NYC"},
            "geometry": {
                "type": "Point",
                "coordinates": [-74.0060, 40.7128]
            }
        }
    ]
}

# Import GeoJSON
gdf = gpd.read_file('data.geojson')
```

## Web Mapping

```python
import folium

# Create map from GeoDataFrame
m = gdf.explore(
    column='value',
    cmap='viridis',
    popup=True,
    tooltip=True,
    tiles='OpenStreetMap'
)

# Add layers
other_gdf.explore(m=m, color='red', name='layer2')

# Save
m.save('map.html')
```

## Geocoding Services

```python
from geopy.geocoders import Nominatim, GoogleV3

# Nominatim (free)
gelocator = Nominatim(user_agent='my-app')

# Google (API key required)
glocator = GoogleV3(api_key='key')

# Geocode addresses
location = gelocator.geocode('NYC')
print(location.latitude, location.longitude)

# Reverse geocode
address = gelocator.reverse(f"{lat}, {lon}")
print(address.address)
```

## Tile Services

```python
# Common tile servers
tiles = {
    'OpenStreetMap': 'OpenStreetMap',
    'CartoDB Positron': 'CartoDB positron',
    'Stamen Terrain': 'Stamen Terrain',
    'Satellite': 'Esri.WorldImagery'
}

# Use in Folium
for name, tile in tiles.items():
    m = folium.Map(tiles=tile)
```

## Database Integration

```python
import geopandas as gpd
import sqlalchemy

# PostGIS connection
engine = sqlalchemy.create_engine('postgresql://user:pass@localhost/db')

# Read from PostGIS
gdf = gpd.read_postgis('SELECT * FROM table', engine)

# Write to PostGIS
gdf.to_postgis('table', engine, if_exists='replace')

# Spatial query from DB
query = "SELECT * FROM points WHERE ST_Contains(polygon, point_geom)"
gdf = gpd.read_postgis(query, engine)
```

## Best Practices

- ✅ Validate geometries before API return
- ✅ Use GeoJSON for web transfer
- ✅ Cache expensive operations
- ✅ Paginate results for large datasets
- ✅ Document API endpoints
