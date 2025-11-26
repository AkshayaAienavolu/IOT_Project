import cv2
import time
import sys
import os

# Add src to path
sys.path.append('src')

from face_detector import FaceDetector
from emotion_recognizer import EmotionRecognizer
from wellbeing_advisor import WellbeingAdvisor

class FERApplication:
    """Real-time Facial Emotion Recognition Application"""
    
    def __init__(self, camera_id=0):
        """
        Initialize FER application
        Args:
            camera_id: Camera device ID (0 for default webcam)
        """
        print("=" * 60)
        print("Facial Emotion Recognition - Mental Health Monitor")
        print("=" * 60)
        
        # Initialize components
        print("\nInitializing components...")
        self.face_detector = FaceDetector(method='haar')
        self.emotion_recognizer = EmotionRecognizer()
        self.wellbeing = WellbeingAdvisor()
        
        # Camera setup
        self.camera_id = camera_id
        self.cap = None
        
        # Performance tracking
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # UI settings
        self.show_probabilities = False
        self.show_suggestion = True
        
        print("\n✓ All components initialized successfully!")
        print("\n" + "=" * 60)
        print("CONTROLS:")
        print("  'q' - Quit application")
        print("  's' - Show wellbeing suggestion")
        print("  'p' - Toggle probability display")
        print("  'a' - Show emotion pattern analysis")
        print("  'r' - Reset emotion history")
        print("  't' - Get daily tip")
        print("=" * 60)
    
    def start_camera(self):
        """Initialize camera"""
        print(f"\nStarting camera (ID: {self.camera_id})...")
        
        # Try with DirectShow backend (Windows)
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            print("⚠️  DirectShow failed, trying default...")
            self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            print("❌ Error: Could not open camera")
            print("\nTroubleshooting tips:")
            print("1. Close other apps using the camera")
            print("2. Check Windows camera permissions")
            print("3. Try a different camera_id")
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("✓ Camera started successfully")
        return True
    
    def calculate_fps(self):
        """Calculate current FPS"""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        return self.fps
    
    def draw_ui(self, frame, emotion, confidence, probabilities):
        """
        Draw UI elements on frame
        Args:
            frame: Input frame
            emotion: Detected emotion
            confidence: Confidence score
            probabilities: All emotion probabilities
        """
        h, w = frame.shape[:2]
        
        # FPS counter
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Main emotion display (top-right)
        if emotion:
            color = self.emotion_recognizer.get_emotion_color(emotion)
            text = f"{emotion}: {confidence*100:.1f}%"
            
            # Background rectangle
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
            cv2.rectangle(frame, (w - text_size[0] - 20, 10),
                         (w - 10, 50), (0, 0, 0), -1)
            
            # Text
            cv2.putText(frame, text, (w - text_size[0] - 15, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
        
        # Probability bars (left side)
        if self.show_probabilities and probabilities is not None:
            y_offset = 60
            bar_width = 150
            bar_height = 20
            
            for i, (em, prob) in enumerate(zip(self.emotion_recognizer.emotions, probabilities)):
                y = y_offset + i * (bar_height + 5)
                
                # Background
                cv2.rectangle(frame, (10, y), (10 + bar_width, y + bar_height),
                            (50, 50, 50), -1)
                
                # Probability bar
                filled_width = int(bar_width * prob)
                color = self.emotion_recognizer.get_emotion_color(em)
                cv2.rectangle(frame, (10, y), (10 + filled_width, y + bar_height),
                            color, -1)
                
                # Label
                cv2.putText(frame, f"{em}: {prob*100:.0f}%",
                           (10 + bar_width + 10, y + 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Instructions (bottom)
        instructions = "Press 's' for suggestion | 'a' for analysis | 'q' to quit"
        cv2.putText(frame, instructions, (10, h - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        """Main application loop"""
        if not self.start_camera():
            return
        
        print("\nStarting real-time emotion recognition...")
        print("Look at the camera and see your emotions detected!\n")
        
        current_emotion = None
        current_confidence = 0
        current_probs = None
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Failed to grab frame")
                    break
                
                # Mirror frame for more natural interaction
                frame = cv2.flip(frame, 1)
                
                # Detect faces
                faces = self.face_detector.detect_faces(frame)
                
                # Process each detected face
                for (x1, y1, x2, y2) in faces:
                    # Ensure valid coordinates
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                    
                    # Extract face region
                    face_roi = frame[y1:y2, x1:x2]
                    
                    if face_roi.size > 0 and face_roi.shape[0] > 0 and face_roi.shape[1] > 0:
                        # Predict emotion
                        emotion, confidence, probs = \
                            self.emotion_recognizer.predict_emotion(face_roi)
                        
                        current_emotion = emotion
                        current_confidence = confidence
                        current_probs = probs
                        
                        # Draw bounding box with emotion color
                        color = self.emotion_recognizer.get_emotion_color(emotion)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                        
                        # Draw emotion label on face
                        label = f"{emotion}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                        
                        # Background for label
                        cv2.rectangle(frame, (x1, y1 - 35), (x1 + label_size[0] + 10, y1),
                                    (0, 0, 0), -1)
                        
                        # Label text
                        cv2.putText(frame, label, (x1 + 5, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                # Calculate FPS
                self.calculate_fps()
                
                # Draw UI
                frame = self.draw_ui(frame, current_emotion, current_confidence, current_probs)
                
                # Display frame
                cv2.imshow('Facial Emotion Recognition - Mental Health Monitor', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n👋 Quitting application...")
                    break
                    
                elif key == ord('s'):
                    if current_emotion:
                        suggestion = self.wellbeing.get_suggestion(current_emotion)
                        print(f"\n{'='*60}")
                        print(f"💡 WELLBEING SUGGESTION")
                        print(f"{'='*60}")
                        print(f"Detected: {current_emotion} ({current_confidence*100:.1f}%)")
                        print(f"Suggestion: {suggestion}")
                        print(f"{'='*60}\n")
                    else:
                        print("⚠️  No face detected. Please look at the camera.")
                
                elif key == ord('p'):
                    self.show_probabilities = not self.show_probabilities
                    status = "ON" if self.show_probabilities else "OFF"
                    print(f"📊 Probability display: {status}")
                
                elif key == ord('a'):
                    analysis = self.wellbeing.get_pattern_analysis(
                        list(self.emotion_recognizer.emotion_history)
                    )
                    print(f"\n{analysis}")
                
                elif key == ord('r'):
                    self.emotion_recognizer.reset_history()
                    print("🔄 Emotion history reset")
                
                elif key == ord('t'):
                    tip = self.wellbeing.get_daily_tip()
                    print(f"\n💡 Daily Tip: {tip}\n")
        
        except Exception as e:
            print(f"\n❌ Error during execution: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            if self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()
            print("\n✓ Application closed successfully")


if __name__ == "__main__":
    try:
        app = FERApplication(camera_id=0)
        app.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()