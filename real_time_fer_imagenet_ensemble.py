"""
Real-time FER with Cross-Dataset Ensemble
FER2013 + ImageNet for True Generalization
"""

import cv2
import time
import sys
import numpy as np

sys.path.append('src')

from face_detector import FaceDetector
from cross_dataset_ensemble_imagenet import CrossDatasetEnsemble
from wellbeing_advisor import WellbeingAdvisor

class ImageNetEnsembleFERApp:
    """Application with true cross-dataset generalization"""
    
    def __init__(self, camera_id=0):
        print("=" * 70)
        print("CROSS-DATASET FACIAL EMOTION RECOGNITION")
        print("ImageNet (14M) + FER2013 (35K) Ensemble")
        print("=" * 70)
        
        print("\nInitializing...")
        self.face_detector = FaceDetector(method='haar')
        self.emotion_recognizer = CrossDatasetEnsemble()
        self.wellbeing = WellbeingAdvisor()
        
        self.camera_id = camera_id
        self.cap = None
        
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        self.show_individual = True
        
        info = self.emotion_recognizer.get_ensemble_info()
        print(f"\n{'='*70}")
        print("ENSEMBLE CONFIGURATION")
        print(f"{'='*70}")
        for i, (model, dataset) in enumerate(zip(info['models'], info['datasets']), 1):
            print(f"{i}. {model}")
            print(f"   {dataset}")
        print(f"\nTotal: {info['total_images']} images")
        
        print("\n✓ Ready!")
        print("\n" + "=" * 70)
        print("CONTROLS:")
        print("  'q' - Quit | 's' - Suggestion | 'i' - Toggle models")
        print("  'a' - Analysis | 'r' - Reset")
        print("=" * 70)
    
    def start_camera(self):
        print(f"\nStarting camera...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print("❌ Camera error")
            return False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("✓ Camera ready")
        return True
    
    def calculate_fps(self):
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        return self.fps
    
    def draw_ui(self, frame, emotion, confidence, individual_preds, agreement):
        h, w = frame.shape[:2]
        
        # FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Dataset info
        cv2.putText(frame, "Cross-Dataset: ImageNet + FER2013", (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Main emotion
        if emotion:
            color = self.emotion_recognizer.get_emotion_color(emotion)
            text = f"{emotion}: {confidence*100:.1f}%"
            
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
            cv2.rectangle(frame, (w - text_size[0] - 20, 10),
                         (w - 10, 50), (0, 0, 0), -1)
            cv2.putText(frame, text, (w - text_size[0] - 15, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
            
            # Agreement
            agreement_color = (0, 255, 0) if agreement > 0.7 else (0, 165, 255)
            status = "AGREE" if agreement > 0.7 else "DIFFER"
            cv2.putText(frame, f"Models: {status}", (w - 200, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, agreement_color, 2)
        
        # Individual predictions
        if self.show_individual and individual_preds:
            y = h - 100
            cv2.rectangle(frame, (5, y-30), (320, h-5), (0, 0, 0), -1)
            
            cv2.putText(frame, "Individual Predictions:", (10, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # FER2013 prediction
            fer_idx = np.argmax(individual_preds[0])
            fer_emotion = self.emotion_recognizer.emotions[fer_idx]
            fer_conf = individual_preds[0][fer_idx]
            cv2.putText(frame, f"FER2013 Scratch: {fer_emotion} ({fer_conf*100:.0f}%)",
                       (10, y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 200, 255), 1)
            
            # ImageNet prediction
            img_idx = np.argmax(individual_preds[1])
            img_emotion = self.emotion_recognizer.emotions[img_idx]
            img_conf = individual_preds[1][img_idx]
            cv2.putText(frame, f"ImageNet Transfer: {img_emotion} ({img_conf*100:.0f}%)",
                       (10, y+35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 255, 200), 1)
        
        # Instructions
        cv2.putText(frame, "Press 's' for suggestion | 'i' for models | 'q' to quit",
                   (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        if not self.start_camera():
            return
        
        print("\nStarting cross-dataset emotion recognition...")
        print("Leveraging ImageNet + FER2013 diversity!\n")
        
        current_emotion = None
        current_confidence = 0
        individual_preds = None
        agreement = None
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                faces = self.face_detector.detect_faces(frame)
                
                for (x1, y1, x2, y2) in faces:
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                    
                    face_roi = frame[y1:y2, x1:x2]
                    
                    if face_roi.size > 0:
                        emotion, confidence, probs, individual, agreement = \
                            self.emotion_recognizer.predict_emotion(face_roi)
                        
                        current_emotion = emotion
                        current_confidence = confidence
                        individual_preds = individual
                        
                        color = self.emotion_recognizer.get_emotion_color(emotion)
                        thickness = 3 if agreement > 0.7 else 2
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                        
                        label = f"{emotion}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                        cv2.rectangle(frame, (x1, y1 - 35), 
                                    (x1 + label_size[0] + 10, y1), (0, 0, 0), -1)
                        cv2.putText(frame, label, (x1 + 5, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                self.calculate_fps()
                frame = self.draw_ui(frame, current_emotion, current_confidence, 
                                    individual_preds, agreement)
                
                cv2.imshow('Cross-Dataset FER - ImageNet + FER2013', frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n👋 Quitting...")
                    break
                
                elif key == ord('s'):
                    if current_emotion:
                        suggestion = self.wellbeing.get_suggestion(current_emotion)
                        print(f"\n{'='*70}")
                        print(f"💡 WELLBEING SUGGESTION")
                        print(f"{'='*70}")
                        print(f"Cross-Dataset Detected: {current_emotion} ({current_confidence*100:.1f}%)")
                        print(f"Model Agreement: {'High' if agreement > 0.7 else 'Moderate'}")
                        print(f"Suggestion: {suggestion}")
                        print(f"{'='*70}\n")
                    else:
                        print("⚠️  No face detected")
                
                elif key == ord('i'):
                    self.show_individual = not self.show_individual
                    print(f"🔍 Individual models: {'ON' if self.show_individual else 'OFF'}")
                
                elif key == ord('a'):
                    analysis = self.wellbeing.get_pattern_analysis(
                        list(self.emotion_recognizer.emotion_history)
                    )
                    print(f"\n{analysis}")
                
                elif key == ord('r'):
                    self.emotion_recognizer.reset_history()
                    print("🔄 History reset")
        
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            if self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()
            print("\n✓ Closed")


if __name__ == "__main__":
    try:
        app = ImageNetEnsembleFERApp(camera_id=0)
        app.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()