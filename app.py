from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest
import tensorflow as tf
from PIL import Image
import numpy as np

app = Flask(__name__)

# AWS S3 configuration
MODEL_PATH = "cats_vs_dogs_model.h5"

# Prometheus metrics
inference_requests = Counter('inference_requests_total', 'Total number of inference requests')
inference_latency = Histogram('inference_latency_seconds', 'Latency of inference requests')

# Load model from S3
model = tf.keras.models.load_model(MODEL_PATH)

# Preprocess function
def preprocess_image(image, target_size=(128, 128)):
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(target_size)
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

# Prediction route
@app.route("/predict", methods=["POST"])
@inference_latency.time()  # Track inference latency
def predict():
    inference_requests.inc()  # Increment inference request count

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    image = Image.open(file)
    processed_image = preprocess_image(image)
    
    prediction = model.predict(processed_image)
    label = "cat" if prediction[0][0] < 0.5 else "dog"
    
    return jsonify({"prediction": label})

# Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
