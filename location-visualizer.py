import folium
from folium.plugins import HeatMap
import pandas as pd

def visualize_movements(df):
    # Create a map centered on the mean latitude and longitude
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    map = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    # Add markers for each location
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}<br>{row['place_name']}<br>{row['address']}"
        ).add_to(map)

    # Add a line connecting all points
    locations = df[['latitude', 'longitude']].values.tolist()
    folium.PolyLine(locations, weight=2, color='red').add_to(map)

    # Add a heatmap layer
    HeatMap(locations).add_to(map)

    # Save the map
    map.save('movement_visualization.html')

# Usage
base_path = 'data'  # Replace with the path to your 'data' folder
df = parse_location_files(base_path)
visualize_movements(df)
print("Map saved as 'movement_visualization.html'")
