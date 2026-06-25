# Interactive Mapping

## Folium

Create interactive web maps:

```python
import folium
import geopandas as gpd

# Create map centered at location
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Save
m.save('map.html')
```

## GeoDataFrame to Map

```python
# Simple GeoDataFrame map
m = gdf.explore()
m.save('map.html')

# With styling
m = gdf.explore(
    column='value',
    cmap='viridis',
    legend=True,
    popup=True,
    tooltip=True
)
```

## Markers and Popups

```python
import folium

m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Simple marker
folium.Marker(
    location=[40.7128, -74.0060],
    popup='NYC',
    tooltip='Click me'
).add_to(m)

# Circle marker (with radius)
folium.CircleMarker(
    location=[40.7128, -74.0060],
    radius=20,
    popup='NYC',
    color='red',
    fill=True,
    fillColor='blue'
).add_to(m)

# Marker with info
folium.Marker(
    location=[40.7128, -74.0060],
    popup=folium.Popup('New York City', max_width=200),
    icon=folium.Icon(color='blue', icon='info-sign')
).add_to(m)
```

## Choropleth Maps

Color by value:

```python
# GeoJSON choropleth
m = folium.Map(location=[40, -95], zoom_start=4)

folium.Choropleth(
    geo_data='us-states.json',
    name='choropleth',
    data=df,
    columns=['state', 'value'],
    key_on='feature.properties.name',
    fill_color='YlGn',
    legend_name='Population'
).add_to(m)

m.save('choropleth.html')
```

## Heatmaps

```python
from folium.plugins import HeatMap

m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Heat map from points
heat_data = [[row.geometry.y, row.geometry.x] for idx, row in gdf.iterrows()]

HeatMap(heat_data).add_to(m)

m.save('heatmap.html')
```

## Layer Control

Toggle layers:

```python
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Add multiple layers
gdf1.explore(m=m, name='Layer 1', color='red')
gdf2.explore(m=m, name='Layer 2', color='blue')

# Add layer control
folium.LayerControl().add_to(m)

m.save('layers.html')
```

## Styling

```python
# Style GeoDataFrame features
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

for idx, row in gdf.iterrows():
    folium.GeoJson(
        data=row.geometry.__geo_interface__,
        style_function=lambda x: {
            'fillColor': 'red' if row['value'] > 100 else 'blue',
            'color': 'black',
            'weight': 2,
            'opacity': 0.8
        }
    ).add_to(m)

m.save('styled.html')
```

## Advanced Features

### Clustering

```python
from folium.plugins import MarkerCluster

m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

mc = MarkerCluster()

for idx, row in gdf.iterrows():
    mc.add_child(
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=row['name']
        )
    )

mc.add_to(m)
m.save('clustered.html')
```

### Rectangle/Circle Drawing

```python
from folium.plugins import Draw

m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

Draw(export=True).add_to(m)

m.save('draw.html')
```

### Mouse Position

```python
from folium.plugins import MousePosition

m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

MousePosition().add_to(m)

m.save('mousepos.html')
```

## Leaflet.js

Native JavaScript mapping:

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
    <div id="map" style="height: 600px;"></div>
    <script>
        const map = L.map('map').setView([40.7128, -74.0060], 12);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        L.marker([40.7128, -74.0060]).addTo(map).bindPopup('NYC');
    </script>
</body>
</html>
```

## Mapbox Integration

```python
import folium

m = folium.Map(
    location=[40.7128, -74.0060],
    zoom_start=12,
    tiles='https://api.mapbox.com/styles/v1/{id}/static/{lon},{lat},{z},{width},{height}@2x?access_token={accessToken}',
    attr='Mapbox',
    API_key='your-mapbox-key'
)

m.save('mapbox.html')
```

## OpenStreetMap Tiles

```python
import folium

m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Different tile styles
folium.TileLayer('OpenStreetMap').add_to(m)
folium.TileLayer('CartoDB positron').add_to(m)
folium.TileLayer('CartoDB voyager').add_to(m)
folium.TileLayer('Stamen Terrain').add_to(m)

folium.LayerControl().add_to(m)
m.save('tiles.html')
```

## Performance Tips

- Use tile layers (not raster)
- Simplify geometries for large datasets
- Use clustering for many points
- Use GeoJSON for vector data
- Cache map renders
- Limit popup sizes
