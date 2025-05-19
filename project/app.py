from flask import Flask, request, jsonify
from flask_cors import CORS
from generate_description import generate_property_description, get_nearby_places_summary

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "🏠 Property Description Generator API is live!"

@app.route('/generate-description', methods=['POST'])
def generate_description():
    try:
        form_data = request.form.to_dict()
        image_files = request.files.getlist("images")

        print("[INFO] Received form data:", form_data)
        print(f"[INFO] Received {len(image_files)} image(s)")

        # Use Geoapify to fetch only nearby place names + distances
        nearby_places_text = get_nearby_places_summary(form_data.get("address"))

        # Generate final property description with OpenAI
        property_description = generate_property_description(form_data, image_files, nearby_places_text)

        return jsonify({
            "description": property_description
        })

    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
