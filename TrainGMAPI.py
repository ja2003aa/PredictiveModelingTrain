API_KEY = 'APIKEY'
import os
import googlemaps
import requests
import polyline

gmaps = googlemaps.Client(key=API_KEY)

def get_directions(origin, destination):
    # Get directions with transit mode set to train
    directions_result = gmaps.directions(
        origin,
        destination,
        mode="transit",
        transit_mode="train",
        departure_time="now" 
    )
    return directions_result

def generate_static_map_url(origin, destination):
    # Get directions
    directions = get_directions(origin, destination)
    
    if not directions:
        print("No directions found")
        return None
    
    # Extract the overview polyline
    route_polyline = directions[0]['overview_polyline']['points']
    
    # Create the Static Map URL
    static_map_url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"size=600x400&"
        f"path=enc:{route_polyline}&"
        f"markers=color:blue|label:S|{origin}&"
        f"markers=color:red|label:D|{destination}&"
        f"key={API_KEY}"
    )
    
    return static_map_url

def save_image_from_url(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join("C:\\Users\\james\\Documents\\Coding\\Chatbot\\Images", "route_map.png")
        with open(file_path, 'wb') as file:
            file.write(response.content)
            file.close()
        print(f"Image saved as {file_name}")
    else:
        print("Failed to retrieve the image")

if __name__ == "__main__":
    origin = "Truro, UK"
    destination = "Norwich Station, UK"
    
    static_map_url = generate_static_map_url(origin, destination)
    if static_map_url:
        print(f"Static Map URL: {static_map_url}")
        save_image_from_url(static_map_url, "route_map.png")
