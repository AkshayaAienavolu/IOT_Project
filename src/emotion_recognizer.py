import numpy as np
import cv2
import tensorflow as tf
from collections import deque

class EmotionRecognizer:
    """Emotion recognition from facial images"""
    
    def __init__(self, model_path='models/fer_model_best.h5'):
        """
        Initialize emotion recognizer
        Args:
            model_path: Path to trained model file
        """
        print(f"Loading emotion recognition model from {model_path}...")
        self.model = tf.keras.models.load_model(model_path)
        print("✓ Model loaded successfully")
        
        # Emotion labels (must match training order)
        self.emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 
                        'Neutral', 'Sad', 'Surprise']
        
        # Emotion history for smoothing
        self.emotion_history = deque(maxlen=10)
        
        # Color mapping for each emotion
        self.emotion_colors = {
            'Angry': (0, 0, 255),      # Red
            'Disgust': (0, 128, 0),    # Dark Green
            'Fear': (128, 0, 128),     # Purple
            'Happy': (0, 255, 0),      # Green
            'Neutral': (128, 128, 128),# Gray
            'Sad': (255, 0, 0),        # Blue
            'Surprise': (0, 255, 255)  # Yellow
        }
    
    def preprocess_face(self, face_img):
        """
        Preprocess face image for model input
        Args:
            face_img: Face region (BGR image)
        Returns:
            Preprocessed image ready for prediction
        """
        # Convert to grayscale
        if len(face_img.shape) == 3:
            face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            face_gray = face_img
        
        # Resize to model input size
        face_resized = cv2.resize(face_gray, (48, 48))
        
        # Normalize pixel values
        face_normalized = face_resized.astype('float32') / 255.0
        
        # Add channel and batch dimensions
        face_input = np.expand_dims(face_normalized, axis=-1)  # Add channel
        face_input = np.expand_dims(face_input, axis=0)        # Add batch
        
        return face_input
    
    def predict_emotion(self, face_img, use_smoothing=True):
        """
        Predict emotion from face image
        Args:
            face_img: Face region (BGR image)
            use_smoothing: Whether to use temporal smoothing
        Returns:
            (emotion, confidence, all_probabilities)
        """
        # Preprocess
        processed = self.preprocess_face(face_img)
        
        # Predict
        predictions = self.model.predict(processed, verbose=0)
        probabilities = predictions[0]
        
        # Get emotion with highest probability
        emotion_idx = np.argmax(probabilities)
        confidence = probabilities[emotion_idx]
        emotion = self.emotions[emotion_idx]
        
        # Apply temporal smoothing
        if use_smoothing:
            self.emotion_history.append(emotion)
            # Use most frequent emotion from history
            if len(self.emotion_history) >= 5:
                emotion = max(set(self.emotion_history), 
                            key=list(self.emotion_history).count)
        
        return emotion, confidence, probabilities
    
    def get_emotion_color(self, emotion):
        """Get color for emotion visualization"""
        return self.emotion_colors.get(emotion, (255, 255, 255))
    
    def get_dominant_emotion(self, window=None):
        """
        Get most frequent emotion from history
        Args:
            window: Number of recent frames to consider (None = all)
        Returns:
            Most frequent emotion
        """
        if not self.emotion_history:
            return None
        
        history = list(self.emotion_history)
        if window:
            history = history[-window:]
        
        return max(set(history), key=history.count)
    
    def get_emotion_distribution(self):
        """
        Get distribution of emotions from history
        Returns:
            Dictionary with emotion counts
        """
        from collections import Counter
        
        if not self.emotion_history:
            return {}
        
        counts = Counter(self.emotion_history)
        total = len(self.emotion_history)
        
        # Convert to percentages
        distribution = {emotion: (count / total * 100) 
                       for emotion, count in counts.items()}
        
        return distribution
    
    def reset_history(self):
        """Clear emotion history"""
        self.emotion_history.clear()