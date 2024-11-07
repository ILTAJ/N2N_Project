from flask import Flask, request, jsonify, render_template_string
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from prometheus_client import Counter, Histogram, generate_latest

# Define constants to match training
IMG_SIZE = (128, 128)

# Load model
model = tf.keras.models.load_model('cats_vs_dogs_model.keras')

# Initialize Flask app
app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('predict_requests', 'Total number of predictions')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Latency of requests')

# HTML template remains the same as before
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Cat vs Dog Predictor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-container { margin: 20px 0; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }
        .result { margin-top: 20px; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Cat vs Dog Image Classifier</h1>
    
    <div class="form-container">
        <h2>Upload an Image</h2>
        <form action="/v1/predict" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*" required>
            <button type="submit">Predict</button>
        </form>
    </div>

    <h2>API Endpoints:</h2>
    <ul>
        <li><code>/v1/predict</code> - POST endpoint for image prediction</li>
        <li><code>/metrics</code> - Prometheus metrics endpoint</li>
    </ul>

    <h2>Usage:</h2>
    <p>Upload an image of a cat or dog, and the model will predict which one it is.</p>
    <p>For API usage, send a POST request to <code>/v1/predict</code> with an image file in the form data.</p>
</body>
</html>
'''

def preprocess_image(image_bytes):
    try:
        # Open the image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if it's not
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to match the training size
        image = image.resize(IMG_SIZE)
        
        # Convert to numpy array and rescale exactly as in training
        img_array = np.array(image)
        img_array = img_array / 255.0  # Same rescaling as used in training
        
        # Ensure the shape is correct (128, 128, 3)
        if img_array.shape != (*IMG_SIZE, 3):
            raise ValueError(f"Processed image shape {img_array.shape} doesn't match required shape {(*IMG_SIZE, 3)}")
        
        return img_array

    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/v1/predict', methods=['POST'])
@REQUEST_LATENCY.time()
def predict():
    REQUEST_COUNT.inc()
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file'].read()
        img = preprocess_image(file)
        
        # Add batch dimension
        img_batch = np.expand_dims(img, axis=0)
        
        # Make prediction
        prediction = model.predict(img_batch, verbose=0)
        confidence = float(prediction[0])  # Convert to float
        label = 'Dog' if confidence > 0.5 else 'Cat'
        
        # If the request wants JSON, return JSON
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'label': label,
                'confidence': confidence,
                'prediction_value': confidence
            })
        
        # Otherwise, return HTML response
        result_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prediction Result</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .result {{ margin: 20px 0; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }}
                .back-button {{ margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="result">
                <h2>Prediction Result:</h2>
                <p>Predicted Class: <strong>{label}</strong></p>
                <p>Confidence: <strong>{confidence:.2%}</strong></p>
                <p>Raw Prediction Value: <strong>{confidence:.4f}</strong></p>
            </div>
            <div class="back-button">
                <a href="/">← Back to Upload Form</a>
            </div>
        </body>
        </html>
        '''
        return result_html

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/metrics')
def metrics():
    return generate_latest()

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Print model information for verification
    print(f"Expected input shape: {(*IMG_SIZE, 3)}")
    print("\nModel Summary:")
    model.summary()
    
    app.run(host='0.0.0.0', port=8081, debug=True)