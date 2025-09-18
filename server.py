from flask import Flask, request, jsonify, render_template
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
from datetime import datetime
import random
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    MODEL_FOLDER = 'models'
    
    # Model configurations
    MODEL_CONFIG = {
        'model1': {
            'name': 'Multi-Crop Analysis',
            'model_path': 'models/model1_multicrop.h5',
            'description': 'Advanced detection for fruits, vegetables & field crops',
            'classes': [
                'apple_scab', 'apple_black_rot', 'apple_cedar_rust', 'apple_healthy',
                'cherry_powdery_mildew', 'cherry_healthy',
                'corn_gray_leaf_spot', 'corn_common_rust', 'corn_northern_leaf_blight', 'corn_healthy',
                'grape_black_rot', 'grape_black_measles', 'grape_leaf_blight', 'grape_healthy',
                'peach_bacterial_spot', 'peach_healthy',
                'orange_haunglongbing', 'orange_healthy',
                'pepper_bacterial_spot', 'pepper_healthy',
                'potato_early_blight', 'potato_late_blight', 'potato_healthy',
                'soybean_healthy',
                'raspberry_healthy',
                'strawberry_leaf_scorch', 'strawberry_healthy',
                'tomato_bacterial_spot', 'tomato_early_blight', 'tomato_late_blight', 
                'tomato_leaf_mold', 'tomato_septoria_leaf_spot', 'tomato_spider_mites',
                'tomato_target_spot', 'tomato_yellow_leaf_curl_virus', 'tomato_mosaic_virus', 'tomato_healthy'
            ],
            'image_size': (224, 224),
            'input_channels': 3
        },
        'model2': {
            'name': 'Staple Crops Analysis',
            'model_path': 'models/model2_staple_crops.h5',
            'description': 'Specialized for major grain and cash crops',
            'classes': [
                'wheat_brown_rust', 'wheat_yellow_rust', 'wheat_stripe_rust', 'wheat_powdery_mildew', 'wheat_healthy',
                'maize_blight', 'maize_common_rust', 'maize_gray_leaf_spot', 'maize_northern_corn_leaf_blight', 'maize_healthy',
                'cotton_bacterial_blight', 'cotton_curl_virus', 'cotton_fusarium_wilt', 'cotton_healthy',
                'sugarcane_mosaic', 'sugarcane_red_rot', 'sugarcane_rust', 'sugarcane_smut', 'sugarcane_healthy',
                'rice_bacterial_blight', 'rice_blast', 'rice_brown_spot', 'rice_tungro', 'rice_sheath_blight', 'rice_healthy'
            ],
            'image_size': (224, 224),
            'input_channels': 3
        },
        'model3': {
            'name': 'Banana Crop Analysis',
            'model_path': 'models/model3_banana.h5',
            'description': 'Specialized banana disease detection and analysis',
            'classes': [
                'banana_black_sigatoka', 'banana_yellow_sigatoka', 'banana_panama_disease', 
                'banana_bract_mosaic_virus', 'banana_bunchy_top_virus', 'banana_healthy'
            ],
            'image_size': (224, 224),
            'input_channels': 3
        }
    }

# Load configuration
app.config.from_object(Config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

# Mock model manager for testing
class MockModelManager:
    def __init__(self, config):
        self.config = config
        self.models = {}
        logger.info("MockModelManager initialized - using simulated models for testing")
    
    def is_model_available(self, model_id):
        return model_id in self.config
    
    def get_available_models(self):
        available = []
        for model_id, config in self.config.items():
            model_info = {
                'id': model_id,
                'name': config['name'],
                'description': config.get('description', ''),
                'available': True,  # Mock all as available
                'classes_count': len(config['classes']),
                'image_size': config['image_size']
            }
            available.append(model_info)
        return available

# Initialize mock model manager
model_manager = MockModelManager(app.config['MODEL_CONFIG'])

# Treatment recommendations
TREATMENT_RECOMMENDATIONS = {
    'apple_scab': 'Apply preventive fungicide sprays containing Captan, Mancozeb, or Strobilurin fungicides during wet spring conditions.',
    'corn_common_rust': 'Plant resistant hybrids when available. Apply fungicides (Triazole or Strobilurin) if infection occurs before tasseling.',
    'tomato_early_blight': 'Apply fungicides containing Chlorothalonil, Mancozeb, or Copper compounds. Provide adequate plant spacing.',
    'wheat_stripe_rust': 'Apply fungicides containing Triazole compounds at first sign of infection. Use resistant varieties.',
    'banana_black_sigatoka': 'Apply systemic fungicides on rotation schedule. Remove infected leaves regularly.',
    'default_healthy': 'Continue current management practices. Monitor plants regularly for early disease detection.',
    'default_diseased': 'Consult with local agricultural extension services for specific treatment protocols.'
}

def get_treatment_recommendation(predicted_class):
    """Get treatment recommendation for a disease"""
    if predicted_class in TREATMENT_RECOMMENDATIONS:
        return TREATMENT_RECOMMENDATIONS[predicted_class]
    elif 'healthy' in predicted_class.lower():
        return TREATMENT_RECOMMENDATIONS['default_healthy']
    else:
        return TREATMENT_RECOMMENDATIONS['default_diseased']

@app.route('/')
def index():
    """Serve the main frontend page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Frontend Not Found</h1>
        <p>Please make sure index.html is in the same directory as server.py</p>
        <p><a href="/api/health">Check API Health</a></p>
        """

@app.route('/api/analyze-leaf', methods=['POST'])
def analyze_leaf():
    """Main endpoint for leaf analysis - Mock version for testing"""
    try:
        logger.info("Received analysis request")
        
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Get model ID
        model_id = request.form.get('model', 'model1')
        if model_id not in app.config['MODEL_CONFIG']:
            return jsonify({'error': f'Invalid model: {model_id}'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
        file_extension = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
        if file_extension not in allowed_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        logger.info(f"Processing image: {image_file.filename} with model: {model_id}")
        
        # Simulate processing delay
        time.sleep(2)
        
        # Get model config for mock response
        config = app.config['MODEL_CONFIG'][model_id]
        
        # Generate realistic mock results
        mock_diseases = {
            'model1': ['apple_scab', 'tomato_early_blight', 'corn_common_rust', 'apple_healthy', 'tomato_healthy'],
            'model2': ['wheat_stripe_rust', 'rice_blast', 'cotton_bacterial_blight', 'wheat_healthy', 'rice_healthy'], 
            'model3': ['banana_black_sigatoka', 'banana_panama_disease', 'banana_healthy']
        }
        
        diseases = mock_diseases.get(model_id, config['classes'])
        selected_disease = random.choice(diseases)
        is_healthy = 'healthy' in selected_disease.lower()
        
        # Calculate mock metrics
        if is_healthy:
            damage_percentage = random.randint(0, 15)
            severity_level = 'Minimal'
            health_status = 'Healthy'
            detected_disease = None
        else:
            damage_percentage = random.randint(25, 75)
            if damage_percentage < 30:
                severity_level = 'Mild'
            elif damage_percentage < 55:
                severity_level = 'Moderate'
            else:
                severity_level = 'Severe'
            health_status = 'Diseased'
            # Format disease name
            parts = selected_disease.split('_')[1:]
            detected_disease = ' '.join(word.capitalize() for word in parts)
        
        # Mock response
        response = {
            'healthStatus': health_status,
            'damagePercentage': damage_percentage,
            'severityLevel': severity_level,
            'leafAreaIndex': str(round(random.uniform(1.5, 4.0), 1)),
            'detectedDisease': detected_disease,
            'recommendation': get_treatment_recommendation(selected_disease),
            'confidence': round(random.uniform(75, 95), 1),
            'model_used': config['name'],
            'predicted_class': selected_disease
        }
        
        logger.info(f"Mock analysis completed: {health_status}, {damage_percentage}% damage")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in analyze_leaf: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """Get list of available models"""
    try:
        models_info = model_manager.get_available_models()
        return jsonify({'models': models_info})
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return jsonify({'error': 'Failed to get models list'}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'models_loaded': 3,  # Mock value
        'timestamp': datetime.now().isoformat(),
        'mode': 'mock_testing'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'models_loaded': 3,  # Mock value
            'total_models': len(app.config['MODEL_CONFIG']),
            'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
            'model_folder_exists': os.path.exists(app.config['MODEL_FOLDER']),
            'mode': 'mock_testing'
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
        'tensorflow_version': tf.__version__,
        'models_initialized': True,
        'timestamp': datetime.now().isoformat()
    })

# Serve static files
@app.route('/app.js')
def serve_app_js():
    """Serve the JavaScript file"""
    try:
        with open('app.js', 'r', encoding='utf-8') as f:
            response = app.response_class(
                response=f.read(),
                status=200,
                mimetype='application/javascript'
            )
            return response
    except FileNotFoundError:
        return "// app.js not found", 404

# Error handlers
@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'error': 'File too large',
        'max_size': f"{app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB"
    }), 413

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting AI Leaf Health Assessment Backend...")
    logger.info(f"TensorFlow version: {tf.__version__}")
    logger.info("Running in MOCK MODE - using simulated models for testing")
    
    # Create directories if they don't exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting server on http://localhost:{port}")
    logger.info("Frontend available at: http://localhost:5000")
    logger.info("API health check: http://localhost:5000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=port)