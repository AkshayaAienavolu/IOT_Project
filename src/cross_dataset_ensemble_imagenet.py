"""
Cross-Dataset Ensemble Recognizer
Combines FER2013-only + ImageNet-pretrained models
"""

import numpy as np
import cv2
import tensorflow as tf
from collections import deque

class CrossDatasetEnsemble:
    """
    Ensemble for true cross-dataset generalization
    Model 1: FER2013 trained from scratch (grayscale, 48x48)
    Model 2: ImageNet pre-trained + FER2013 fine-tuned (RGB, 96x96)
    """
    
    def __init__(self):
        print("Initializing Cross-Dataset Ensemble...")
        
        self.emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 
                        'Neutral', 'Sad', 'Surprise']
        
        # Load FER2013 model (grayscale)
        print("  [1/2] Loading FER2013 model (from scratch)...")
        self.fer_model = tf.keras.models.load_model('models/fer_model_best.h5')
        print("      OK FER2013 model loaded")
        print("        Input: 48x48 grayscale")
        print("        Training: FER2013 only (35K images)")
        
        # Load MobileNet model (RGB)
        print("  [2/2] Loading MobileNet model (ImageNet base)...")
        self.mobilenet_model = tf.keras.models.load_model(
            'models/pretrained/mobilenetv3_finetuned.h5'
        )
        print("      OK MobileNet model loaded")
        print("        Input: 96x96 RGB")
        print("        Base: ImageNet (14M images)")
        print("        Fine-tuned: FER2013 (35K images)")
        
        print("\nOK Cross-dataset ensemble ready!")
        print("  Total training data: 14M + 35K images")
        print("  Datasets: ImageNet + FER2013")
        
        # Model weights (can be tuned)
        self.weights = {
            'fer2013': 0.4,      # From-scratch model
            'imagenet': 0.6      # Pre-trained model (often better)
        }
        
        self.emotion_history = deque(maxlen=10)
        
        self.emotion_colors = {
            'Angry': (0, 0, 255), 'Disgust': (0, 128, 0),
            'Fear': (128, 0, 128), 'Happy': (0, 255, 0),
            'Neutral': (128, 128, 128), 'Sad': (255, 0, 0),
            'Surprise': (0, 255, 255)
        }
    
    def preprocess_fer(self, face_img):
        """Preprocess for FER2013 model (grayscale, 48x48)"""
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img
        resized = cv2.resize(gray, (48, 48))
        normalized = resized.astype('float32') / 255.0
        return np.expand_dims(np.expand_dims(normalized, axis=-1), axis=0)
    
    def preprocess_mobilenet(self, face_img):
        """Preprocess for MobileNet model (RGB, 96x96)"""
        if len(face_img.shape) == 2:
            rgb = cv2.cvtColor(face_img, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (96, 96))
        normalized = resized.astype('float32') / 255.0
        return np.expand_dims(normalized, axis=0)
    
    def predict_emotion(self, face_img, use_smoothing=True):
        """
        Predict using cross-dataset ensemble
        Returns: (emotion, confidence, probs, individual_preds, agreement)
        """
        # Predict with FER2013 model
        fer_input = self.preprocess_fer(face_img)
        fer_probs = self.fer_model.predict(fer_input, verbose=0)[0]
        
        # Predict with MobileNet model
        mobilenet_input = self.preprocess_mobilenet(face_img)
        mobilenet_probs = self.mobilenet_model.predict(mobilenet_input, verbose=0)[0]
        
        # Ensemble prediction (weighted average)
        ensemble_probs = (
            self.weights['fer2013'] * fer_probs +
            self.weights['imagenet'] * mobilenet_probs
        )
        
        # Get final emotion
        emotion_idx = np.argmax(ensemble_probs)
        confidence = ensemble_probs[emotion_idx]
        emotion = self.emotions[emotion_idx]
        
        # Calculate agreement
        fer_pred = self.emotions[np.argmax(fer_probs)]
        mobilenet_pred = self.emotions[np.argmax(mobilenet_probs)]
        agreement = 1.0 if fer_pred == mobilenet_pred else 0.5
        
        # Temporal smoothing
        if use_smoothing:
            self.emotion_history.append(emotion)
            if len(self.emotion_history) >= 5:
                emotion = max(set(self.emotion_history), 
                            key=list(self.emotion_history).count)
                confidence = list(self.emotion_history).count(emotion) / len(self.emotion_history)
        
        individual_preds = [fer_probs, mobilenet_probs]
        
        return emotion, confidence, ensemble_probs, individual_preds, agreement
    
    def get_emotion_color(self, emotion):
        return self.emotion_colors.get(emotion, (255, 255, 255))
    
    def get_dominant_emotion(self, window=None):
        if not self.emotion_history:
            return None
        history = list(self.emotion_history)
        if window:
            history = history[-window:]
        return max(set(history), key=history.count)
    
    def reset_history(self):
        self.emotion_history.clear()
    
    def get_ensemble_info(self):
        return {
            'models': ['FER2013 (Scratch)', 'ImageNet+FER2013 (Transfer)'],
            'datasets': ['FER2013: 35K', 'ImageNet: 14M + FER2013: 35K'],
            'weights': self.weights,
            'total_images': '14M + 35K',
            'type': 'Cross-Dataset Ensemble'
        }
