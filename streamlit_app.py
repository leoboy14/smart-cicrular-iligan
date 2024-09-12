import streamlit as st
from streamlit_folium import folium_static
import folium

# Set page config to wide mode
st.set_page_config(layout="wide")

# Create a map centered on Iligan City
m = folium.Map(location=[8.2280, 124.2452], zoom_start=12, control_scale=True)

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
        tooltip=name
    ).add_to(m)

# Display the map
folium_static(m, width=1600, height=800)

# Add a title and description
st.markdown("""
    <div style='position: absolute; top: 10px; left: 10px; z-index: 1000; background-color: rgba(255, 255, 255, 0.7); padding: 10px; border-radius: 5px;'>
        <h1>Iligan City Interactive Map</h1>
        <p>Click on markers to learn about key locations in Iligan City.</p>
    </div>
""", unsafe_allow_html=True)