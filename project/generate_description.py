import os
import openai
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

# Encode image to base64
def encode_image_file(file_storage):
    return base64.b64encode(file_storage.read()).decode('utf-8')

# Convert address to latitude and longitude using Geoapify Geocoding API
def get_coordinates_from_address(address):
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": address,
        "apiKey": GEOAPIFY_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    features = data.get("features")
    if features and len(features) > 0:
        geometry = features[0].get("geometry", {})
        coordinates = geometry.get("coordinates", [])
        if len(coordinates) == 2:
            lon, lat = coordinates
            return lat, lon
    return None, None

# Use Geoapify Places API to get nearby places with names and distances only
def get_nearby_places_summary(address):
    lat, lon = get_coordinates_from_address(address)
    if not lat or not lon:
        return "Nearby places data unavailable due to address issue."

    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "commercial.supermarket,education.university,healthcare.hospital,leisure.park",
        "filter": f"circle:{lon},{lat},3000",
        "bias": f"proximity:{lon},{lat}",
        "limit": 5,
        "apiKey": GEOAPIFY_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    places = []
    for feature in data.get("features", []):
        prop = feature.get("properties", {})
        name = prop.get("name")
        distance = prop.get("distance")
        if name and distance:
            places.append(f"{name} ({int(distance)} meters away)")

    if not places:
        return "No notable places found nearby within 3 km."
    return "Nearby places include: " + ", ".join(places) + "."

# Generate the property description using GPT
def generate_property_description(form_data, image_files, nearby_places_text):
    images = [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image_file(image)}"
            }
        }
        for image in image_files
    ]

    prompt = f"""
Generate a real estate property listing using the following information.

Property Details:
- Bedrooms: {form_data.get('beds')}
- Bathrooms: {form_data.get('baths')}
- Receptions: {form_data.get('receptions')}
- Property Type: {form_data.get('property_type')}
- Furnishing: {form_data.get('furnishing')}
- Address: {form_data.get('address')}
- Location: {form_data.get('location')}
- Key Features: {form_data.get('key_features')}
- Additional Info: {form_data.get('details')}

Nearby Amenities:
{nearby_places_text}

Generate structured property listing content including:

Title:

Format: <number of bedrooms> <property type> for sale <street name>, <area/town/city> <postcode>
Example: 3 bed semi-detached house for sale Portland Avenue, New Malden KT3

Short Description:

Length: 50~100 words
Content: Summary of the property layout and features (e.g. number of bedrooms, garden, kitchen, parking, etc.)
Tone: Neutral and factual
Do not include emotional or promotional phrases (e.g., “perfect for families”, “ideal location”, “beautifully presented”)

Full Description:

Length: 500~1000 words
Content:
Describe the property layout, room-by-room, floor-by-floor
Mention features, dimensions (if provided), appliances, storage, outdoor spaces, parking, and development/building features
Include only factual and verifiable details
Mention location benefits in a factual tone (e.g., proximity to stations, local amenities)
including all property and nearby places info. Use UK tone, no promotional hype.

Tone:
Neutral, semi-professional, and UK real estate specific
No promotional or emotional language
Do not invent or assume user preferences
Avoid adjectives like “stunning”, “inviting”, “charming”, “ideal”, “luxurious”
Do not add fictional context or elaborate beyond the given data
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": images + [{"type": "text", "text": prompt}]
            }
        ],
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message.content
