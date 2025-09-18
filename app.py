from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import json
import cv2
from werkzeug.utils import secure_filename
import logging
from config import Config
from model_utils import ModelManager, ImageProcessor, PredictionAnalyzer, get_treatment_recommendation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load configuration
app.config.from_object(Config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

# Initialize model manager and processors
model_manager = None
image_processor = ImageProcessor()
prediction_analyzer = PredictionAnalyzer()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Leaf Health Assessment - Backend</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-3xl font-bold text-center mb-8 text-green-800">
                🌿 AI Leaf Health Assessment - Backend
            </h1>
            
            <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4">API Status</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <h3 class="font-medium text-blue-800">Server Status</h3>
                        <p class="text-2xl font-bold text-blue-600">✅ Running</p>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg">
                        <h3 class="font-medium text-green-800">Models Loaded</h3>
                        <p class="text-2xl font-bold text-green-600" id="models-count">{{ models_loaded }}</p>
                    </div>
                    <div class="bg-yellow-50 p-4 rounded-lg">
                        <h3 class="font-medium text-yellow-800">Total Models</h3>
                        <p class="text-2xl font-bold text-yellow-600">{{ total_models }}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4">Available Models</h2>
                <div class="space-y-3" id="models-list">
                    {% for model in models %}
                    <div class="flex items-center justify-between p-3 border rounded-lg
                                {% if model.available %}bg-green-50 border-green-200{% else %}bg-red-50 border-red-200{% endif %}">
                        <div>
                            <h3 class="font-medium">{{ model.name }}</h3>
                            <p class="text-sm text-gray-600">Classes: {{ model.classes_count }}</p>
                        </div>
                        <span class="px-3 py-1 rounded-full text-sm font-medium
                                   {% if model.available %}bg-green-200 text-green-800{% else %}bg-red-200 text-red-800{% endif %}">
                            {% if model.available %}Available{% else %}Not Loaded{% endif %}
                        </span>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-xl font-semibold mb-4">API Endpoints</h2>
                <div class="space-y-4">
                    <div class="border-l-4 border-blue-500 pl-4">
                        <h3 class="font-medium">POST /api/analyze-leaf</h3>
                        <p class="text-sm text-gray-600">Upload leaf image for analysis</p>
                        <p class="text-xs text-gray-500">Parameters: image (file), model (string)</p>
                    </div>
                    <div class="border-l-4 border-green-500 pl-4">
                        <h3 class="font-medium">GET /api/models</h3>
                        <p class="text-sm text-gray-600">Get available models</p>
                    </div>
                    <div class="border-l-4 border-purple-500 pl-4">
                        <h3 class="font-medium">GET /api/health</h3>
                        <p class="text-sm text-gray-600">Health check endpoint</p>
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-8">
                <p class="text-gray-600">© 2025 Smart AgriTech Platform | Backend Service</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

def initialize_models():
    """Initialize model manager and load models"""
    global model_manager
    try:
        model_manager = ModelManager(app.config['MODEL_CONFIG'])
        logger.info(f"Model manager initialized with {len(model_manager.models)} models loaded")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize models: {str(e)}")
        return False

@app.route('/')
def index():
    """Root endpoint with API information"""
    if model_manager is None:
        models_info = []
        models_loaded = 0
    else:
        models_info = model_manager.get_available_models()
        models_loaded = len(model_manager.models)
    
    total_models = len(app.config['MODEL_CONFIG'])
    
    return render_template_string(
        HTML_TEMPLATE,
        models=models_info,
        models_loaded=models_loaded,
        total_models=total_models
    )

@app.route('/api/analyze-leaf', methods=['POST'])
def analyze_leaf():
    """Main endpoint for leaf analysis"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Get model ID
        model_id = request.form.get('model', 'model1')  # Default to model1
        if model_id not in app.config['MODEL_CONFIG']:
            return jsonify({'error': f'Invalid model: {model_id}'}), 400
        
        # Check if models are initialized
        if model_manager is None:
            logger.error("Model manager not initialized")
            return jsonify({'error': 'Models not loaded. Please check server logs.'}), 500
        
        # Check if specific model is available
        if not model_manager.is_model_available(model_id):
            logger.warning(f"Model {model_id} not available")
            return jsonify({
                'error': f'Model {model_id} not available. Please check if model file exists.',
                'available_models': [m['id'] for m in model_manager.get_available_models() if m['available']]
            }), 404
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
        file_extension = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
        if file_extension not in allowed_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(f"{model_id}_{image_file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            image_file.save(filepath)
            
            # Get model and config
            model = model_manager.get_model(model_id)
            config = app.config['MODEL_CONFIG'][model_id]
            
            # Preprocess image
            processed_image = image_processor.preprocess_for_model(filepath, config['image_size'])
            if processed_image is None:
                return jsonify({'error': 'Failed to process image. Please check image format.'}), 400
            
            # Make prediction
            logger.info(f"Making prediction with {config['name']}")
            predictions = model.predict(processed_image, verbose=0)
            
            # Analyze predictions
            predicted_class_idx = np.argmax(predictions[0])
            predicted_class = config['classes'][predicted_class_idx]
            confidence = float(predictions[0][predicted_class_idx])
            
            # Calculate metrics
            damage_percentage = prediction_analyzer.calculate_damage_percentage(
                predictions, config['classes'], filepath
            )
            severity_level = prediction_analyzer.get_severity_level(damage_percentage)
            health_status = prediction_analyzer.get_health_status(predicted_class)
            lai = image_processor.calculate_leaf_area_index(filepath)
            
            # Get disease name and recommendation
            disease_name = prediction_analyzer.format_disease_name(predicted_class)
            recommendation = get_treatment_recommendation(predicted_class)
            
            # Prepare response
            response = {
                'healthStatus': health_status,
                'damagePercentage': damage_percentage,
                'severityLevel': severity_level,
                'leafAreaIndex': str(lai),
                'detectedDisease': disease_name,
                'recommendation': recommendation,
                'confidence': round(confidence * 100, 2),
                'model_used': config['name'],
                'predicted_class': predicted_class
            }
            
            logger.info(f"Analysis completed successfully for {filename}")
            logger.info(f"Results: {health_status}, {damage_percentage}% damage, {severity_level} severity")
            
            return jsonify(response)
        
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
        
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error in analyze_leaf: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """Get list of available models"""
    try:
        if model_manager is None:
            return jsonify({
                'models': [],
                'error': 'Models not initialized'
            })
        
        models_info = model_manager.get_available_models()
        return jsonify({'models': models_info})
    
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return jsonify({'error': 'Failed to get models list'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        models_loaded = len(model_manager.models) if model_manager else 0
        total_models = len(app.config['MODEL_CONFIG'])
        
        return jsonify({
            'status': 'healthy',
            'models_loaded': models_loaded,
            'total_models': total_models,
            'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
            'model_folder_exists': os.path.exists(app.config['MODEL_FOLDER'])
        })
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for API connectivity"""
    return jsonify({
        'message': 'API is working!',
        'timestamp': tf.__version__,
        'tensorflow_version': tf.__version__,
        'models_initialized': model_manager is not None
    })

# Error handlers
@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'error': 'File too large',
        'max_size': f"{app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB"
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.before_first_request
def startup():
    """Initialize models before first request"""
    logger.info("Initializing application...")
    success = initialize_models()
    if not success:
        logger.warning("Failed to load some or all models. Check model files.")

if __name__ == '__main__':
    # Initialize models
    logger.info("Starting AI Leaf Health Assessment Backend...")
    logger.info(f"TensorFlow version: {tf.__version__}")
    
    # Create directories if they don't exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Initialize models
    initialize_models()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on port {port}")
    app.run(debug=debug, host='0.0.0.0', port=port)