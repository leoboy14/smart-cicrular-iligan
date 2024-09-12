import streamlit as st
from streamlit_folium import folium_static
import folium
from folium import plugins
import kml2geojson
import os
from shapely.geometry import shape, mapping
import random

# Set page config to wide mode
st.set_page_config(layout="wide")

# Force a refresh by adding a random parameter
refresh_param = random.randint(1, 1000000)

# Define a dark theme for the map using a custom TileLayer
dark_theme = folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    name='Dark Theme',
    control=False,
    tms=False
)

# Create a map centered on Iligan City
m = folium.Map(location=[8.2280, 124.2452], zoom_start=12, control_scale=True)

# Add the dark theme layer
dark_theme.add_to(m)

# Add markers with tooltips for notable locations
locations = {
    "Iligan City Hall": (8.2283, 124.2450, "The seat of the city government of Iligan."),
    "Maria Cristina Falls": (8.1917, 124.1967, "Also known as the 'twin falls', it's the primary source of electric power for the city's industries."),
    "Tinago Falls": (8.1661, 124.2067, "A hidden waterfall, its name 'Tinago' means 'hidden' in Filipino."),
    "Mindanao State University - Iligan Institute of Technology": (8.2375, 124.2447, "A major state university in the Philippines, known for its engineering programs."),
    "Iligan Bay": (8.2166, 124.2000, "The bay area of Iligan City, part of Iligan Bay."),
    "Mandulog River": (8.2047, 124.2364, "One of the major rivers in Iligan City."),
    "Lanao del Norte Provincial Capitol": (8.2280, 124.2444, "The seat of the provincial government of Lanao del Norte."),
    "Anahaw Amphitheater": (8.2381, 124.2447, "An open-air amphitheater located within the MSU-IIT campus."),
    "Iligan City National High School": (8.2308, 124.2447, "One of the largest public high schools in the city."),
    "St. Michael's Cathedral": (8.2275, 124.2447, "The mother church of the Roman Catholic Diocese of Iligan.")
}

for name, info in locations.items():
    lat, lon, description = info
    folium.Marker(
        [lat, lon],
        popup=folium.Popup(description, max_width=300),
        tooltip=name,
        icon=folium.Icon(color='lightgray', icon='info-sign')
    ).add_to(m)

# Function to simplify geometry
def simplify_geometry(geom, tolerance=0.0001):
    if geom['type'] == 'Polygon':
        return mapping(shape(geom).simplify(tolerance))
    elif geom['type'] == 'MultiPolygon':
        simple_polys = [shape(poly).simplify(tolerance) for poly in geom['coordinates']]
        return mapping(shapely.geometry.MultiPolygon(simple_polys))
    return geom

# Convert KML to GeoJSON and simplify geometries
kml_file = "admin-map-KML.kml"  # Make sure this file is in the same directory as your script
if not os.path.exists(kml_file):
    st.error(f"KML file '{kml_file}' not found. Please make sure it's in the same directory as this script.")
else:
    try:
        # Convert KML to GeoJSON
        geojson = kml2geojson.main.convert(kml_file)
        
        # Simplify geometries
        for feature in geojson[0]['features']:
            if 'geometry' in feature and feature['geometry'] is not None:
                feature['geometry'] = simplify_geometry(feature['geometry'])
        
        # Add GeoJSON to the map with red border
        style_function = lambda x: {
            'fillColor': '#000000',
            'color': '#FF0000',
            'fillOpacity': 0.1,
            'weight': 2
        }

        folium.GeoJson(
            geojson[0],
            name="KML Data",
            style_function=style_function
        ).add_to(m)

    except Exception as e:
        st.error(f"An error occurred while processing the KML file: {str(e)}")

# Add layer control and fullscreen option
folium.LayerControl().add_to(m)
plugins.Fullscreen().add_to(m)

# Display the map
folium_static(m, width=1600, height=800)

# Add a title and description with light text for dark background
st.markdown(f"""
    <div style='position: absolute; top: 10px; left: 10px; z-index: 1000; background-color: rgba(0, 0, 0, 0.7); padding: 10px; border-radius: 5px;'>
        <h1 style='color: white;'>Iligan City Interactive Map</h1>
        <p style='color: #cccccc;'>Click on markers to learn about key locations in Iligan City. The KML data is displayed as an additional layer with red borders.</p>
        <p style='color: #cccccc;'>Refresh: {refresh_param}</p>
    </div>
""", unsafe_allow_html=True)

# Force a rerun to update the map
st.experimental_rerun()