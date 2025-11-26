import cv2
import numpy as np

class FaceDetector:
    """Face detection using OpenCV Haar Cascade or DNN"""
    
    def __init__(self, method='haar'):
        """
        Initialize face detector
        Args:
            method: 'haar' for Haar Cascade (faster) or 'dnn' for DNN (more accurate)
        """
        self.method = method
        
        if method == 'haar':
            # Load Haar Cascade classifier
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.detector = cv2.CascadeClassifier(cascade_path)
            print("✓ Face detector initialized (Haar Cascade)")
            
        elif method == 'dnn':
            # Load DNN face detector
            modelFile = "opencv_face_detector_uint8.pb"
            configFile = "opencv_face_detector.pbtxt"
            try:
                self.detector = cv2.dnn.readNetFromTensorflow(modelFile, configFile)
                print("✓ Face detector initialized (DNN)")
            except:
                print("⚠ DNN model not found, falling back to Haar Cascade")
                self.method = 'haar'
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.detector = cv2.CascadeClassifier(cascade_path)
    
    def detect_faces(self, frame):
        """
        Detect faces in frame
        Args:
            frame: Input image/frame
        Returns:
            List of bounding boxes [(x1, y1, x2, y2), ...]
        """
        if self.method == 'haar':
            return self._detect_haar(frame)
        else:
            return self._detect_dnn(frame)
    
    def _detect_haar(self, frame):
        """Detect faces using Haar Cascade"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Convert to (x1, y1, x2, y2) format
        boxes = []
        for (x, y, w, h) in faces:
            boxes.append((x, y, x + w, y + h))
        
        return boxes
    
    def _detect_dnn(self, frame):
        """Detect faces using DNN"""
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
        
        self.detector.setInput(blob)
        detections = self.detector.forward()
        
        boxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                x1 = int(detections[0, 0, i, 3] * w)
                y1 = int(detections[0, 0, i, 4] * h)
                x2 = int(detections[0, 0, i, 5] * w)
                y2 = int(detections[0, 0, i, 6] * h)
                boxes.append((x1, y1, x2, y2))
        
        return boxes
    
    def draw_faces(self, frame, boxes, color=(0, 255, 0), thickness=2):
        """Draw bounding boxes on frame"""
        for (x1, y1, x2, y2) in boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        return frame