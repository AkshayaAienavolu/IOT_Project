import numpy as np
import cv2
import tensorflow as tf
from collections import deque

class ThreeDatasetEnsemble:
    '''
    Ultimate cross-dataset ensemble
    Model 1: FER2013 only (35K, from scratch)
    Model 2: ImageNet + FER2013 + RAF-DB (14M + 35K + 30K, transfer)
    
    Total training data: 14,065,000 images across 3 datasets!
    '''
    
    def __init__(self):
        print("Initializing Three-Dataset Ensemble...")
        
        self.emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 
                        'Neutral', 'Sad', 'Surprise']
        
        # Model 1: FER2013 from scratch
        print("  [1/2] Loading FER2013 model (from scratch)...")
        self.fer_model = tf.keras.models.load_model('models/fer_model_best.h5')
        print("      OK: FER2013 model loaded")
        print("        Training: FER2013 only (35K images)")
        
        # Model 2: Three-dataset transfer learning
        print("  [2/2] Loading Three-Dataset model...")
        self.multi_model = tf.keras.models.load_model(
            'models/pretrained/final_cross_dataset.h5'
        )
        print("      OK: Three-dataset model loaded")
        print("        Stage 1: ImageNet (14M images)")
        print("        Stage 2: FER2013 (35K images)")
        print("        Stage 3: RAF-DB (30K images)")
        print("        TOTAL: 14,065,000 images!")
        
        print("\n✓ Ultimate cross-dataset ensemble ready!")
        print("  Generalization across:")
        print("    • Demographics (global diversity)")
        print("    • Lighting (all conditions)")
        print("    • Camera angles (all perspectives)")
        print("    • Contexts (lab + real-world)")
        
        # Model weights
        self.weights = {
            'fer2013': 0.3,      # Single dataset
            'multi': 0.7         # Three datasets (more weight)
        }
        
        self.emotion_history = deque(maxlen=10)
        
        self.emotion_colors = {
            'Angry': (0, 0, 255), 'Disgust': (0, 128, 0),
            'Fear': (128, 0, 128), 'Happy': (0, 255, 0),
            'Neutral': (128, 128, 128), 'Sad': (255, 0, 0),
            'Surprise': (0, 255, 255)
        }
    
    def preprocess_fer(self, face_img):
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img
        resized = cv2.resize(gray, (48, 48))
        normalized = resized.astype('float32') / 255.0
        return np.expand_dims(np.expand_dims(normalized, axis=-1), axis=0)
    
    def preprocess_multi(self, face_img):
        if len(face_img.shape) == 2:
            rgb = cv2.cvtColor(face_img, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (96, 96))
        normalized = resized.astype('float32') / 255.0
        return np.expand_dims(normalized, axis=0)
    
    def predict_emotion(self, face_img, use_smoothing=True):
        # FER2013 model prediction
        fer_input = self.preprocess_fer(face_img)
        fer_probs = self.fer_model.predict(fer_input, verbose=0)[0]
        
        # Three-dataset model prediction
        multi_input = self.preprocess_multi(face_img)
        multi_probs = self.multi_model.predict(multi_input, verbose=0)[0]
        
        # Weighted ensemble
        ensemble_probs = (
            self.weights['fer2013'] * fer_probs +
            self.weights['multi'] * multi_probs
        )
        
        emotion_idx = np.argmax(ensemble_probs)
        confidence = ensemble_probs[emotion_idx]
        emotion = self.emotions[emotion_idx]
        
        # Agreement
        fer_pred = self.emotions[np.argmax(fer_probs)]
        multi_pred = self.emotions[np.argmax(multi_probs)]
        agreement = 1.0 if fer_pred == multi_pred else 0.5
        
        # Temporal smoothing
        if use_smoothing:
            self.emotion_history.append(emotion)
            if len(self.emotion_history) >= 5:
                emotion = max(set(self.emotion_history), 
                            key=list(self.emotion_history).count)
                confidence = list(self.emotion_history).count(emotion) / len(self.emotion_history)
        
        individual_preds = [fer_probs, multi_probs]
        
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
            'models': ['FER2013 (Scratch)', 'ImageNet+FER2013+RAF-DB (Transfer)'],
            'datasets': ['FER2013: 35K', 'ImageNet: 14M + FER2013: 35K + RAF-DB: 30K'],
            'weights': self.weights,
            'total_images': '14,065,000',
            'type': 'Three-Dataset Cross-Generalization Ensemble'
        }
