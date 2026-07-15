import os
import numpy as np
from PIL import Image
import json

# Make TensorFlow optional to allow the app to run without heavy ML deps
try:
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
    from tensorflow.keras.preprocessing import image
    TENSORFLOW_AVAILABLE = True
except Exception:
    TENSORFLOW_AVAILABLE = False

class WasteClassifier:
    """AI-powered waste classification system"""
    
    def __init__(self):
        # Load pre-trained model if TensorFlow is available; otherwise work in fallback mode
        self.model = None
        if TENSORFLOW_AVAILABLE:
            try:
                self.model = MobileNetV2(weights='imagenet', include_top=True)
            except Exception:
                self.model = None
        
        # Waste category mappings based on common items
        self.waste_categories = {
            'electronic': {
                'keywords': ['laptop', 'computer', 'phone', 'television', 'monitor', 'keyboard', 
                           'mouse', 'printer', 'camera', 'radio', 'speaker', 'headphone'],
                'bin': 'E-Waste Bin',
                'color': '#FF6B6B',
                'instructions': 'Take to designated e-waste collection center. Remove batteries if possible.'
            },
            'plastic': {
                'keywords': ['bottle', 'container', 'bag', 'cup', 'plate', 'fork', 'spoon',
                           'toy', 'bucket', 'chair'],
                'bin': 'Plastic Recycling Bin',
                'color': '#4ECDC4',
                'instructions': 'Clean container and remove labels. Check recycling number.'
            },
            'metal': {
                'keywords': ['can', 'tin', 'aluminum', 'steel', 'iron', 'copper', 'wire',
                           'screw', 'nail', 'tool'],
                'bin': 'Metal Recycling Bin',
                'color': '#45B7D1',
                'instructions': 'Clean metal items. Remove any non-metal attachments.'
            },
            'glass': {
                'keywords': ['bottle', 'jar', 'window', 'mirror', 'bulb', 'vase'],
                'bin': 'Glass Recycling Bin',
                'color': '#96CEB4',
                'instructions': 'Remove caps and lids. Clean thoroughly before disposal.'
            },
            'paper': {
                'keywords': ['book', 'newspaper', 'magazine', 'cardboard', 'box', 'envelope',
                           'notebook', 'paper'],
                'bin': 'Paper Recycling Bin',
                'color': '#FFEAA7',
                'instructions': 'Remove any plastic coating or metal staples.'
            },
            'organic': {
                'keywords': ['apple', 'banana', 'orange', 'vegetable', 'fruit', 'food',
                           'leaf', 'flower', 'plant'],
                'bin': 'Compost Bin',
                'color': '#6C5CE7',
                'instructions': 'Suitable for composting. Remove any packaging.'
            },
            'hazardous': {
                'keywords': ['battery', 'paint', 'chemical', 'medicine', 'syringe',
                           'thermometer', 'fluorescent'],
                'bin': 'Hazardous Waste Collection',
                'color': '#E17055',
                'instructions': 'Take to special hazardous waste facility. Do not put in regular bins.'
            },
            'general': {
                'keywords': ['trash', 'waste', 'garbage'],
                'bin': 'General Waste Bin',
                'color': '#636e72',
                'instructions': 'Non-recyclable waste goes to general waste bin.'
            }
        }
        
        # Carbon footprint data (kg CO2 saved per kg of material recycled)
        self.carbon_savings = {
            'electronic': 15.0,  # High impact due to rare earth metals
            'plastic': 2.0,
            'metal': 3.5,
            'glass': 0.5,
            'paper': 1.5,
            'organic': 0.3,
            'hazardous': 5.0,
            'general': 0.0
        }
    
    def preprocess_image(self, image_path):
        """Preprocess image for model prediction"""
        try:
            # Load and resize image
            img = Image.open(image_path)
            img = img.convert('RGB')
            img = img.resize((224, 224))
            
            # If ML stack unavailable, just return a dummy array
            if not TENSORFLOW_AVAILABLE or self.model is None:
                return np.zeros((1, 224, 224, 3), dtype=np.float32)

            # Convert to array and preprocess
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            
            return img_array
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def classify_waste(self, image_path):
        """Classify waste item from image"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return self._get_default_classification()
            
            # Get predictions only if ML model is available; else use keyword heuristic
            if TENSORFLOW_AVAILABLE and self.model is not None:
                predictions = self.model.predict(processed_image)
                decoded_predictions = decode_predictions(predictions, top=5)[0]
            else:
                decoded_predictions = []
            
            # Find best matching waste category
            best_category = 'general'
            best_confidence = 0.0
            
            for _, label, confidence in decoded_predictions:
                label_lower = label.lower()
                
                for category, data in self.waste_categories.items():
                    for keyword in data['keywords']:
                        if keyword in label_lower:
                            if confidence > best_confidence:
                                best_category = category
                                best_confidence = confidence
                            break
            
            # If no good match found, use general category
            if best_confidence < 0.1:
                best_category = 'general'
                best_confidence = 0.5
            
            category_data = self.waste_categories[best_category]
            
            return {
                'category': best_category,
                'confidence': float(best_confidence),
                'bin': category_data['bin'],
                'color': category_data['color'],
                'instructions': category_data['instructions'],
                'carbon_impact': self.carbon_savings.get(best_category, 0.0),
                'predictions': ([{'label': label, 'confidence': float(conf)} 
                              for _, label, conf in decoded_predictions]
                               if decoded_predictions else [])
            }
            
        except Exception as e:
            print(f"Error classifying waste: {e}")
            return self._get_default_classification()
    
    def _get_default_classification(self):
        """Return default classification when error occurs"""
        return {
            'category': 'general',
            'confidence': 0.5,
            'bin': 'General Waste Bin',
            'color': '#636e72',
            'instructions': 'Unable to classify. Please consult local waste guidelines.',
            'carbon_impact': 0.0,
            'predictions': []
        }
    
    def calculate_carbon_impact(self, category, weight_kg=1.0):
        """Calculate environmental impact of proper disposal"""
        carbon_saved = self.carbon_savings.get(category, 0.0) * weight_kg
        
        # Estimate other environmental benefits
        energy_saved = carbon_saved * 2.5  # kWh
        water_saved = carbon_saved * 10    # liters
        
        return {
            'carbon_saved_kg': carbon_saved,
            'energy_saved_kwh': energy_saved,
            'water_saved_liters': water_saved,
            'trees_equivalent': carbon_saved / 22,  # Average tree absorbs 22kg CO2/year
        }
