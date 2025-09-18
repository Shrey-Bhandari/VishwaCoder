#!/usr/bin/env python3
"""
Production server startup script for AI Leaf Health Assessment Backend
"""
import os
import sys
import logging
from app import app, initialize_models

def setup_logging():
    """Setup comprehensive logging"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_environment():
    """Check if environment is properly set up"""
    required_dirs = ['uploads', 'models']
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    # Check for model files
    model_files = [
        'models/model1_multicrop.h5',
        'models/model2_staple_crops.h5',
        'models/model3_banana.h5'
    ]
    
    missing_models = [f for f in model_files if not os.path.exists(f)]
    
    if missing_models:
        print("WARNING: The following model files are missing:")
        for model in missing_models:
            print(f"  - {model}")
        print("\nTo use the corresponding models, place your trained .h5 files in the models/ directory")
        print("The application will still run with available models.\n")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🌿 AI Leaf Health Assessment Backend")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check environment
    check_environment()
    
    # Initialize models
    logger.info("Initializing models...")
    initialize_models()
    
    # Get configuration
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    if debug:
        print(f"\nDevelopment server starting...")
        print(f"Access the API at: http://localhost:{port}")
        print(f"API Documentation: http://localhost:{port}")
        print(f"Health Check: http://localhost:{port}/api/health")
        print("\nPress Ctrl+C to stop the server")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()