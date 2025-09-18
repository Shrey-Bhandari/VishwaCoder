import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MODEL_FOLDER = os.environ.get('MODEL_FOLDER') or 'models'
    
    # Model configurations - Updated with more comprehensive disease classes
    MODEL_CONFIG = {
        'model1': {
            'name': 'Multi-Crop Analysis',
            'model_path': 'models/model1_multicrop.h5',
            'description': 'Advanced detection for fruits, vegetables & field crops',
            'classes': [
                # Apple diseases
                'apple_scab', 'apple_black_rot', 'apple_cedar_rust', 'apple_healthy',
                # Cherry diseases
                'cherry_powdery_mildew', 'cherry_healthy',
                # Corn diseases
                'corn_gray_leaf_spot', 'corn_common_rust', 'corn_northern_leaf_blight', 'corn_healthy',
                # Grape diseases
                'grape_black_rot', 'grape_black_measles', 'grape_leaf_blight', 'grape_healthy',
                # Other fruit diseases
                'peach_bacterial_spot', 'peach_healthy',
                'orange_haunglongbing', 'orange_healthy',
                # Vegetable diseases
                'pepper_bacterial_spot', 'pepper_healthy',
                'potato_early_blight', 'potato_late_blight', 'potato_healthy',
                # Other crops
                'soybean_healthy',
                'raspberry_healthy',
                'strawberry_leaf_scorch', 'strawberry_healthy',
                # Tomato diseases (comprehensive)
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
                # Wheat diseases
                'wheat_brown_rust', 'wheat_yellow_rust', 'wheat_stripe_rust', 'wheat_powdery_mildew', 'wheat_healthy',
                # Maize/Corn diseases
                'maize_blight', 'maize_common_rust', 'maize_gray_leaf_spot', 'maize_northern_corn_leaf_blight', 'maize_healthy',
                # Cotton diseases
                'cotton_bacterial_blight', 'cotton_curl_virus', 'cotton_fusarium_wilt', 'cotton_healthy',
                # Sugarcane diseases
                'sugarcane_mosaic', 'sugarcane_red_rot', 'sugarcane_rust', 'sugarcane_smut', 'sugarcane_healthy',
                # Rice diseases
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
    
    # File upload settings
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}
    
    # Model prediction settings
    PREDICTION_THRESHOLD = 0.5
    MAX_PREDICTIONS = 5

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    LOG_LEVEL = 'DEBUG'
    MODEL_CACHE = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    LOG_LEVEL = 'INFO'
    MODEL_CACHE = True
    
    # Security settings for production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production config")

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # Testing-specific settings
    LOG_LEVEL = 'WARNING'
    MODEL_CACHE = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])