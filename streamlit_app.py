import streamlit as st
import folium
from streamlit_folium import folium_static
import kml2geojson
import os
from shapely.geometry import shape, mapping
import pandas as pd
import branca.colormap as cm

# Set page config
st.set_page_config(layout="wide", page_title="Iligan City Waste Map")

# Title
st.title("Iligan City Waste Map")

# Load waste data
@st.cache_data
def load_waste_data():
    return pd.read_csv("iligan_waste_data.csv")

waste_data = load_waste_data()

# Create color map
min_waste = waste_data['waste_amount'].min()
max_waste = waste_data['waste_amount'].max()
colormap = cm.LinearColormap(colors=['green', 'yellow', 'red'], vmin=min_waste, vmax=max_waste)

# Create a map centered on Iligan City
m = folium.Map(location=[8.2280, 124.2452], zoom_start=11)

# Convert KML to GeoJSON for barangay boundaries
admin_kml_file = "admin-map-KML.kml"
if not os.path.exists(admin_kml_file):
    st.error(f"KML file '{admin_kml_file}' not found. Please make sure it's in the same directory as this script.")
else:
    try:
        admin_geojson = kml2geojson.main.convert(admin_kml_file)
        
        # Simplify geometries (if needed)
        def simplify_geometry(geom, tolerance=0.0001):
            if geom['type'] == 'Polygon':
                return mapping(shape(geom).simplify(tolerance))
            elif geom['type'] == 'MultiPolygon':
                simple_polys = [shape(poly).simplify(tolerance) for poly in geom['coordinates']]
                return mapping(shapely.geometry.MultiPolygon(simple_polys))
            return geom
        
        for feature in admin_geojson[0]['features']:
            if 'geometry' in feature and feature['geometry'] is not None:
                feature['geometry'] = simplify_geometry(feature['geometry'])
        
        # Add GeoJSON to the map with color based on waste amount
        def style_function(feature):
            barangay_name = feature['properties'].get('name', '')
            waste_amount = waste_data[waste_data['barangay'] == barangay_name]['waste_amount'].values
            if len(waste_amount) > 0:
                color = colormap(waste_amount[0])
            else:
                color = 'gray'  # Default color if no data available
            return {
                'fillColor': color,
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.7,
            }

        folium.GeoJson(
            admin_geojson[0],
            name="Barangay Boundaries",
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Barangay:'])
        ).add_to(m)

        # Add color legend
        colormap.add_to(m)
        colormap.caption = 'Waste Amount'

        # Convert KML to GeoJSON for BMRF locations
        bmrf_kml_file = "Iligan-BMRF.kml"
        if not os.path.exists(bmrf_kml_file):
            st.error(f"KML file '{bmrf_kml_file}' not found. Please make sure it's in the same directory as this script.")
        else:
            bmrf_geojson = kml2geojson.main.convert(bmrf_kml_file)
            
            # Add markers for each BMRF location
            for feature in bmrf_geojson[0]['features']:
                if feature['geometry']['type'] == 'Point':
                    coordinates = feature['geometry']['coordinates']
                    name = feature['properties'].get('name', 'Unknown')
                    folium.Marker(
                        [coordinates[1], coordinates[0]],
                        popup=name,
                        tooltip=name
                    ).add_to(m)

    except Exception as e:
        st.error(f"An error occurred while processing the KML files: {str(e)}")

# Display the map
folium_static(m)

# Display waste data table
st.subheader("Waste Data by Barangay")
st.dataframe(waste_data)