import openai
import base64
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("")

def encode_image_file(file_storage):
    return base64.b64encode(file_storage.read()).decode('utf-8')

def generate_property_description(form_data, image_files):
    images = [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image_file(image)}"
            }
        }
        for image in image_files
    ]

    context_text = f"""
Property Information:
- Beds: {form_data.get('beds')}
- Baths: {form_data.get('baths')}
- Reception Rooms: {form_data.get('receptions')}
- Property Type: {form_data.get('property_type')}
- Furnishing: {form_data.get('furnishing')}
- Address: {form_data.get('address')}
- Location: {form_data.get('location')}
- Key Features: {form_data.get('key_features')}
- Additional Details: {form_data.get('details')}

generate:
1. A short catchy **Title**
2. A **Short Description** (~50 words)
3. A **Full Description** (~300 words)
"""

    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": images + [{"type": "text", "text": context_text}]
            }
        ],
        max_tokens=700,
        temperature=0.7
    )

    return response.choices[0].message.content
