import json
import pandas as pd
from datetime import datetime
import os
from geopy.distance import geodesic
import folium
from folium.plugins import HeatMap

def parse_location_files(base_path):
    all_data = []
    semantic_location_path = os.path.join(base_path, 'Semantic Location History')
    
    for year_folder in os.listdir(semantic_location_path):
        year_path = os.path.join(semantic_location_path, year_folder)
        if os.path.isdir(year_path):
            for month_file in os.listdir(year_path):
                if month_file.endswith('.json'):
                    file_path = os.path.join(year_path, month_file)
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                    
                    if 'timelineObjects' in data:
                        for item in data['timelineObjects']:
                            try:
                                if 'placeVisit' in item:
                                    location = item['placeVisit']['location']
                                    timestamp = item['placeVisit'].get('duration', {}).get('startTimestamp')
                                    if timestamp:
                                        all_data.append({
                                            'timestamp': datetime.fromisoformat(timestamp.rstrip('Z')),
                                            'latitude': location['latitudeE7'] / 1e7,
                                            'longitude': location['longitudeE7'] / 1e7,
                                            'place_name': location.get('name', 'Unknown'),
                                            'address': location.get('address', 'Unknown')
                                        })
                                elif 'activitySegment' in item:
                                    start_location = item['activitySegment'].get('startLocation', {})
                                    end_location = item['activitySegment'].get('endLocation', {})
                                    start_timestamp = item['activitySegment'].get('duration', {}).get('startTimestamp')
                                    end_timestamp = item['activitySegment'].get('duration', {}).get('endTimestamp')
                                    
                                    if start_timestamp and start_location:
                                        all_data.append({
                                            'timestamp': datetime.fromisoformat(start_timestamp.rstrip('Z')),
                                            'latitude': start_location['latitudeE7'] / 1e7,
                                            'longitude': start_location['longitudeE7'] / 1e7,
                                            'place_name': 'Start of activity',
                                            'address': 'Unknown'
                                        })
                                    
                                    if end_timestamp and end_location:
                                        all_data.append({
                                            'timestamp': datetime.fromisoformat(end_timestamp.rstrip('Z')),
                                            'latitude': end_location['latitudeE7'] / 1e7,
                                            'longitude': end_location['longitudeE7'] / 1e7,
                                            'place_name': 'End of activity',
                                            'address': 'Unknown'
                                        })
                            except KeyError as e:
                                print(f"KeyError in file {file_path}: {str(e)}")
                            except ValueError as e:
                                print(f"ValueError in file {file_path}: {str(e)}")
    
    return pd.DataFrame(all_data).sort_values('timestamp')

def calculate_total_distance(df):
    total_distance = 0
    for i in range(1, len(df)):
        point1 = (df.iloc[i-1]['latitude'], df.iloc[i-1]['longitude'])
        point2 = (df.iloc[i]['latitude'], df.iloc[i]['longitude'])
        total_distance += geodesic(point1, point2).kilometers
    return total_distance

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

def main():
    base_path = 'data'  # Replace with the path to your 'data' folder
    df = parse_location_files(base_path)
    print(df.head())

    total_distance = calculate_total_distance(df)
    print(f"Total distance traveled: {total_distance:.2f} km")

    visualize_movements(df)
    print("Map saved as 'movement_visualization.html'")

if __name__ == "__main__":
    main()
