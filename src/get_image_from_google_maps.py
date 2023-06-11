import requests

def get_image_from_google_maps(center, zoom = "18", size ="640x640",file_name = "map.png"):
    # Set the base URL for the Google Static Maps API
    base_url = "https://maps.googleapis.com/maps/api/staticmap?"
    api_key = 'AIzaSyCAjPeiMtjN6s81j9J1arK4crYnIsWc1wE'
    # Tomer ! make sure you use your own API key

    # Set the image format (png, jpg, gif)
    format = "png"

    # Build the complete URL
    url = f"{base_url}center={center}&zoom={zoom}&size={size}&format={format}&maptype=satellite&scale=2&key={api_key}"

    # Send the request to the Google Static Maps API
    response = requests.get(url)

    # If the request was successful, save the image to a file
    if response.status_code == 200:
        with open(file_name, "wb") as f:
            f.write(response.content)
