import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
import os
import logging
from typing import Optional, Dict, List, Tuple

# Configure logging
logger = logging.getLogger(__name__)

class ModelManager:
    """Manages loading and inference of ML models"""
    
    def __init__(self, model_config: Dict):
        self.model_config = model_config
        self.models = {}
        self.load_all_models()
    
    def load_all_models(self):
        """Load all available models"""
        logger.info("Loading all available models...")
        for model_id, config in self.model_config.items():
            success = self.load_model(model_id)
            if success:
                logger.info(f"✅ {config['name']} loaded successfully")
            else:
                logger.warning(f"⚠️  {config['name']} failed to load")
        
        logger.info(f"Model loading complete. {len(self.models)}/{len(self.model_config)} models loaded.")
    
    def load_model(self, model_id: str) -> bool:
        """Load a specific model"""
        if model_id not in self.model_config:
            logger.error(f"Unknown model ID: {model_id}")
            return False
        
        config = self.model_config[model_id]
        model_path = config['model_path']
        
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}")
            logger.info(f"To use {config['name']}, place your trained model at: {model_path}")
            return False
        
        try:
            # Load model with error handling for different TensorFlow versions
            self.models[model_id] = tf.keras.models.load_model(
                model_path,
                compile=False  # Skip compilation for faster loading
            )
            
            # Verify model input shape
            expected_shape = (None, *config['image_size'], config.get('input_channels', 3))
            actual_shape = self.models[model_id].input_shape
            
            if actual_shape != expected_shape:
                logger.warning(f"Model input shape mismatch. Expected: {expected_shape}, Got: {actual_shape}")
            
            logger.info(f"Successfully loaded {config['name']} model from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load {config['name']} model: {str(e)}")
            logger.error(f"Model path: {model_path}")
            return False
    
    def get_model(self, model_id: str):
        """Get a loaded model"""
        return self.models.get(model_id)
    
    def is_model_available(self, model_id: str) -> bool:
        """Check if model is available"""
        return model_id in self.models
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models"""
        available = []
        for model_id, config in self.model_config.items():
            model_info = {
                'id': model_id,
                'name': config['name'],
                'description': config.get('description', ''),
                'available': model_id in self.models,
                'classes_count': len(config['classes']),
                'image_size': config['image_size']
            }
            available.append(model_info)
        return available
    
    def reload_model(self, model_id: str) -> bool:
        """Reload a specific model"""
        if model_id in self.models:
            del self.models[model_id]
        return self.load_model(model_id)

class ImageProcessor:
    """Handles image preprocessing and analysis"""
    
    @staticmethod
    def preprocess_for_model(image_path: str, target_size: Tuple[int, int]) -> Optional[np.ndarray]:
        """Preprocess image for model prediction"""
        try:
            # Read and validate image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            # Open and convert image
            image = Image.open(image_path)
            
            # Handle different image modes
            if image.mode == 'RGBA':
                # Convert RGBA to RGB by adding white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array and normalize
            image_array = np.array(image, dtype=np.float32) / 255.0
            
            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)
            
            logger.debug(f"Image preprocessed successfully. Shape: {image_array.shape}")
            return image_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            return None
    
    @staticmethod
    def calculate_leaf_area_index(image_path: str) -> float:
        """Calculate Leaf Area Index using image processing"""
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found for LAI calculation: {image_path}")
                return 2.0
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return 2.0
            
            # Convert to HSV for better green detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define range for green color (leaf area)
            # Adjusted ranges for better leaf detection
            lower_green = np.array([35, 40, 40])
            upper_green = np.array([80, 255, 255])
            
            # Create mask for green areas
            mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Apply morphological operations to clean up the mask
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Calculate green area ratio
            green_pixels = cv2.countNonZero(mask)
            total_pixels = mask.shape[0] * mask.shape[1]
            
            if total_pixels == 0:
                return 2.0
            
            green_ratio = green_pixels / total_pixels
            
            # Estimate LAI (scaled to typical range)
            lai = round(green_ratio * 5.0, 1)
            
            # Clamp to reasonable LAI range
            lai = max(0.1, min(lai, 8.0))
            
            logger.debug(f"LAI calculated: {lai} (green ratio: {green_ratio:.3f})")
            return lai
            
        except Exception as e:
            logger.error(f"Error calculating LAI for {image_path}: {str(e)}")
            return 2.0  # Default reasonable value
    
    @staticmethod
    def analyze_disease_severity(image_path: str) -> int:
        """Analyze disease severity using image processing"""
        try:
            if not os.path.exists(image_path):
                return 25
            
            image = cv2.imread(image_path)
            if image is None:
                return 25
            
            # Convert to HSV for better analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define ranges for diseased areas
            diseased_masks = []
            
            # Brown/dead areas
            lower_brown = np.array([8, 50, 20])
            upper_brown = np.array([20, 255, 200])
            brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
            diseased_masks.append(brown_mask)
            
            # Yellow/chlorotic areas
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])
            yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            diseased_masks.append(yellow_mask)
            
            # Dark spots/lesions
            lower_dark = np.array([0, 0, 0])
            upper_dark = np.array([180, 255, 50])
            dark_mask = cv2.inRange(hsv, lower_dark, upper_dark)
            diseased_masks.append(dark_mask)
            
            # Combine all disease masks
            combined_mask = np.zeros_like(brown_mask)
            for mask in diseased_masks:
                combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Apply morphological operations to clean up
            kernel = np.ones((3, 3), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            
            # Calculate diseased area ratio
            diseased_pixels = cv2.countNonZero(combined_mask)
            total_pixels = combined_mask.shape[0] * combined_mask.shape[1]
            
            if total_pixels == 0:
                return 25
            
            diseased_ratio = diseased_pixels / total_pixels
            severity_percentage = int(diseased_ratio * 100)
            
            # Clamp to reasonable range
            severity_percentage = max(5, min(severity_percentage, 90))
            
            logger.debug(f"Disease severity: {severity_percentage}% (diseased ratio: {diseased_ratio:.3f})")
            return severity_percentage
            
        except Exception as e:
            logger.error(f"Error analyzing disease severity for {image_path}: {str(e)}")
            return 25

class PredictionAnalyzer:
    """Analyzes model predictions and generates insights"""
    
    @staticmethod
    def calculate_damage_percentage(predictions: np.ndarray, classes: List[str], image_path: str = None) -> int:
        """Calculate damage percentage from predictions"""
        try:
            predicted_class_idx = np.argmax(predictions[0])
            predicted_class = classes[predicted_class_idx]
            confidence = float(predictions[0][predicted_class_idx])
            
            # Base calculation on prediction
            if 'healthy' in predicted_class.lower():
                # For healthy plants, low damage with some uncertainty factor
                base_damage = max(0, int((1 - confidence) * 20))
                
                # Add image analysis for more accurate assessment
                if image_path:
                    image_damage = ImageProcessor.analyze_disease_severity(image_path)
                    # Weight image analysis lower for healthy predictions
                    final_damage = int((base_damage * 0.7) + (image_damage * 0.3))
                    return min(25, final_damage)  # Cap healthy damage at 25%
                
                return base_damage
            else:
                # For diseased plants, combine confidence with image analysis
                base_damage = int(confidence * 60) + 20  # 20-80% range
                
                if image_path:
                    image_damage = ImageProcessor.analyze_disease_severity(image_path)
                    # Weight both factors for diseased predictions
                    final_damage = int((base_damage * 0.6) + (image_damage * 0.4))
                    return min(95, max(15, final_damage))
                
                return min(90, base_damage)
                
        except Exception as e:
            logger.error(f"Error calculating damage percentage: {str(e)}")
            return 30  # Conservative default
    
    @staticmethod
    def get_severity_level(damage_percentage: int) -> str:
        """Determine severity level from damage percentage"""
        if damage_percentage < 15:
            return "Minimal"
        elif damage_percentage < 30:
            return "Mild"
        elif damage_percentage < 55:
            return "Moderate"
        elif damage_percentage < 75:
            return "Severe"
        else:
            return "Critical"
    
    @staticmethod
    def get_health_status(predicted_class: str) -> str:
        """Determine overall health status"""
        return "Healthy" if 'healthy' in predicted_class.lower() else "Diseased"
    
    @staticmethod
    def format_disease_name(predicted_class: str) -> Optional[str]:
        """Format disease name for display"""
        if 'healthy' in predicted_class.lower():
            return None
        
        try:
            # Split by underscore and process
            parts = predicted_class.split('_')
            
            # Remove crop name (first part) and 'disease'/'virus' suffixes
            disease_parts = []
            for part in parts[1:]:  # Skip crop name
                if part.lower() not in ['disease', 'virus']:
                    disease_parts.append(part)
            
            if not disease_parts:
                disease_parts = parts[1:]  # Fallback to all parts except crop
            
            # Capitalize and join
            formatted = ' '.join(word.capitalize() for word in disease_parts)
            
            # Apply common disease name corrections
            corrections = {
                'Scab': 'Apple Scab',
                'Rust': 'Leaf Rust',
                'Blight': 'Leaf Blight',
                'Spot': 'Leaf Spot',
                'Mildew': 'Powdery Mildew',
                'Sigatoka': 'Sigatoka Disease',
                'Mosaic': 'Mosaic Virus',
                'Curl': 'Leaf Curl Virus',
                'Wilt': 'Fungal Wilt'
            }
            
            for old, new in corrections.items():
                if formatted == old:
                    formatted = new
                    break
            
            return formatted if formatted else "Unknown Disease"
            
        except Exception as e:
            logger.error(f"Error formatting disease name {predicted_class}: {str(e)}")
            return "Disease Detected"

# Comprehensive disease treatment recommendations
TREATMENT_RECOMMENDATIONS = {
    # Apple diseases
    'apple_scab': 'Apply preventive fungicide sprays containing Captan, Mancozeb, or Strobilurin fungicides during wet spring conditions. Remove and destroy fallen leaves. Improve air circulation through proper pruning. Consider resistant varieties for future plantings.',
    
    'apple_black_rot': 'Prune and destroy all infected branches and mummified fruits. Apply copper-based fungicides during dormant season. Ensure proper orchard drainage and avoid overhead irrigation. Remove cankers from trunk and major branches.',
    
    'apple_cedar_rust': 'Remove nearby juniper/cedar trees within 1-2 miles if possible. Apply preventive fungicide sprays (Myclobutanil, Propiconazole) from pink bud stage through petal fall. Use resistant apple varieties.',
    
    # Cherry diseases
    'cherry_powdery_mildew': 'Apply sulfur-based fungicides or systemic fungicides like Myclobutanil. Improve air circulation through proper pruning. Avoid overhead watering. Apply treatments every 7-14 days during humid conditions.',
    
    # Corn/Maize diseases
    'corn_gray_leaf_spot': 'Use resistant hybrid varieties. Practice crop rotation with non-host crops. Apply foliar fungicides (Strobilurin group) if disease pressure is high. Manage crop residue through tillage.',
    
    'corn_common_rust': 'Plant resistant hybrids when available. Apply fungicides (Triazole or Strobilurin) only if infection occurs before tasseling in susceptible varieties. Monitor weather conditions favoring disease.',
    
    'corn_northern_leaf_blight': 'Use resistant varieties as primary control. Apply fungicides during critical growth stages (V8-R1) if conditions favor disease development. Rotate with non-host crops.',
    
    # Tomato diseases
    'tomato_early_blight': 'Apply fungicides containing Chlorothalonil, Mancozeb, or Copper compounds. Provide adequate plant spacing for air circulation. Use drip irrigation to avoid leaf wetness. Remove infected lower leaves.',
    
    'tomato_late_blight': 'Apply preventive fungicides (Metalaxyl + Mancozeb, Cymoxanil). Remove and destroy infected plants immediately. Avoid overhead irrigation. Ensure good drainage and air circulation.',
    
    'tomato_bacterial_spot': 'Use copper-based bactericides. Plant disease-free seeds and transplants. Provide adequate spacing. Avoid working with wet plants. Remove infected plant debris.',
    
    # Rice diseases
    'rice_blast': 'Apply systemic fungicides containing Tricyclazole or Azoxystrobin. Use resistant varieties. Manage nitrogen fertilization - avoid excessive nitrogen. Ensure proper field drainage.',
    
    'rice_bacterial_blight': 'Use resistant varieties as primary control. Apply copper-based bactericides during early infection stages. Avoid excessive nitrogen fertilization. Manage irrigation to prevent prolonged flooding.',
    
    # Wheat diseases
    'wheat_stripe_rust': 'Apply fungicides containing Triazole compounds (Propiconazole, Tebuconazole) at first sign of infection. Use resistant varieties. Monitor weather conditions favoring rust development.',
    
    'wheat_powdery_mildew': 'Apply sulfur-based fungicides or systemic fungicides. Ensure adequate plant spacing. Use resistant varieties. Avoid excessive nitrogen fertilization.',
    
    # Banana diseases
    'banana_black_sigatoka': 'Apply systemic fungicides (Propiconazole, Tebuconazole) on rotation schedule. Remove infected leaves regularly. Improve plantation drainage. Use resistant cultivars where available.',
    
    'banana_panama_disease': 'No chemical control available. Remove and destroy infected plants immediately. Plant resistant varieties (Cavendish alternatives). Improve soil drainage and avoid replanting in infected areas.',
    
    # Cotton diseases
    'cotton_bacterial_blight': 'Use pathogen-free seeds. Apply copper-based bactericides during humid conditions. Provide adequate plant spacing. Avoid overhead irrigation and excessive nitrogen.',
    
    # Default recommendations
    'default_healthy': 'Continue current management practices. Monitor plants regularly for early disease detection. Maintain proper nutrition, irrigation, and cultural practices. Consider preventive treatments during high-risk periods.',
    
    'default_diseased': 'Consult with local agricultural extension services for specific treatment protocols. Implement integrated disease management including resistant varieties, cultural practices, biological controls, and targeted chemical applications. Consider soil health and environmental factors.'
}

def get_treatment_recommendation(predicted_class: str) -> str:
    """Get comprehensive treatment recommendation"""
    try:
        # Direct match
        if predicted_class in TREATMENT_RECOMMENDATIONS:
            return TREATMENT_RECOMMENDATIONS[predicted_class]
        
        # Check if healthy
        if 'healthy' in predicted_class.lower():
            return TREATMENT_RECOMMENDATIONS['default_healthy']
        
        # Try crop-specific matches
        crop_name = predicted_class.split('_')[0] if '_' in predicted_class else ''
        
        # Look for crop-specific recommendations
        crop_matches = [key for key in TREATMENT_RECOMMENDATIONS.keys() 
                       if key.startswith(crop_name) and key != predicted_class]
        
        if crop_matches:
            base_recommendation = TREATMENT_RECOMMENDATIONS[crop_matches[0]]
            return f"{base_recommendation}\n\nNote: Treatment adapted for similar {crop_name} disease. Consult agricultural extension for specific strain identification."
        
        # Disease-type specific recommendations
        disease_keywords = {
            'rust': 'Apply fungicides containing Triazole compounds. Use resistant varieties. Monitor environmental conditions.',
            'blight': 'Apply broad-spectrum fungicides. Improve air circulation and drainage. Remove infected plant material.',
            'spot': 'Use copper-based fungicides or bactericides. Ensure good sanitation practices.',
            'mildew': 'Apply sulfur-based or systemic fungicides. Improve air circulation.',
            'virus': 'Remove infected plants immediately. Control insect vectors. Use virus-free planting material.',
            'wilt': 'Improve soil drainage. Use resistant varieties. Apply appropriate fungicides.'
        }
        
        for keyword, treatment in disease_keywords.items():
            if keyword in predicted_class.lower():
                return f"{treatment}\n\nGeneral recommendation based on disease type. Consult local experts for specific treatment protocols."
        
        return TREATMENT_RECOMMENDATIONS['default_diseased']
        
    except Exception as e:
        logger.error(f"Error getting treatment recommendation for {predicted_class}: {str(e)}")
        return TREATMENT_RECOMMENDATIONS['default_diseased']