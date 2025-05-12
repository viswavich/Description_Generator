from flask import Flask, request, jsonify
from generate_description import generate_property_description

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Server is running. POST to /generate-description with form-data."

@app.route('/generate-description', methods=['POST'])
def generate_description():
    if 'images' not in request.files:
        return jsonify({"error": "No image files uploaded"}), 400

    form_data = request.form.to_dict()
    image_files = request.files.getlist("images")

    try:
        result = generate_property_description(form_data, image_files)
        return jsonify({"output": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
