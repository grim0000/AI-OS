import cv2
import numpy as np
import os
import pickle
import time
from ultralytics import YOLO
from face_recognition import face_encodings, face_locations, compare_faces
import logging
from typing import List, Tuple, Optional
import json

class AdminFaceRecognition:
    def __init__(self, admin_faces_dir: str = "admin_faces", confidence_threshold: float = 0.8):
        """
        Initialize the Admin Face Recognition system
        
        Args:
            admin_faces_dir: Directory containing admin face images
            confidence_threshold: Minimum confidence for face recognition
        """
        self.admin_faces_dir = admin_faces_dir
        self.confidence_threshold = confidence_threshold
        self.known_face_encodings = []
        self.known_face_names = []
        self.admin_encodings = []
        self.admin_names = []
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('admin_face_recognition.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load YOLOv8 model for face detection
        try:
            self.yolo_model = YOLO('yolov8n-face.pt')
            self.logger.info("YOLOv8 face detection model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load YOLOv8 model: {e}")
            self.logger.info("Downloading YOLOv8 face detection model...")
            self.yolo_model = YOLO('yolov8n-face.pt')
        
        # Create admin faces directory if it doesn't exist
        os.makedirs(admin_faces_dir, exist_ok=True)
        
        # Load admin face encodings
        self.load_admin_faces()
        
    def load_admin_faces(self):
        """Load admin face encodings from the admin_faces directory"""
        try:
            if not os.path.exists(self.admin_faces_dir):
                self.logger.warning(f"Admin faces directory {self.admin_faces_dir} not found")
                return
            
            # Load face encodings from pickle file if it exists
            encodings_file = os.path.join(self.admin_faces_dir, "admin_encodings.pkl")
            if os.path.exists(encodings_file):
                with open(encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.admin_encodings = data['encodings']
                    self.admin_names = data['names']
                    self.logger.info(f"Loaded {len(self.admin_encodings)} admin face encodings")
                    return
            
            # Process admin face images
            for filename in os.listdir(self.admin_faces_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(self.admin_faces_dir, filename)
                    self.add_admin_face(image_path, filename.split('.')[0])
                    
        except Exception as e:
            self.logger.error(f"Error loading admin faces: {e}")
    
    def add_admin_face(self, image_path: str, admin_name: str):
        """
        Add a new admin face to the system
        
        Args:
            image_path: Path to the admin face image
            admin_name: Name of the admin
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to load image: {image_path}")
                return False
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces using YOLOv8
            results = self.yolo_model(rgb_image)
            
            if len(results) == 0:
                self.logger.warning(f"No faces detected in {image_path}")
                return False
            
            # Get the first detected face
            face_location = results[0].boxes.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, face_location)
            
            # Extract face region
            face_image = rgb_image[y1:y2, x1:x2]
            
            # Generate face encoding
            face_encoding = face_encodings(face_image)
            
            if len(face_encoding) == 0:
                self.logger.warning(f"Could not generate encoding for face in {image_path}")
                return False
            
            # Add to admin encodings
            self.admin_encodings.append(face_encoding[0])
            self.admin_names.append(admin_name)
            
            # Save encodings to pickle file
            self.save_admin_encodings()
            
            self.logger.info(f"Added admin face: {admin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding admin face: {e}")
            return False
    
    def save_admin_encodings(self):
        """Save admin face encodings to pickle file"""
        try:
            data = {
                'encodings': self.admin_encodings,
                'names': self.admin_names
            }
            encodings_file = os.path.join(self.admin_faces_dir, "admin_encodings.pkl")
            with open(encodings_file, 'wb') as f:
                pickle.dump(data, f)
            self.logger.info("Admin face encodings saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving admin encodings: {e}")
    
    def recognize_admin_face(self, frame: np.ndarray) -> Tuple[bool, Optional[str], float]:
        """
        Recognize if the face in the frame belongs to an admin
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Tuple of (is_admin, admin_name, confidence)
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces using YOLOv8
            results = self.yolo_model(rgb_frame)
            
            if len(results) == 0:
                return False, None, 0.0
            
            # Process each detected face
            for result in results:
                boxes = result.boxes
                if len(boxes) == 0:
                    continue
                
                # Get face location and confidence
                box = boxes[0]
                face_location = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                
                if confidence < self.confidence_threshold:
                    continue
                
                x1, y1, x2, y2 = map(int, face_location)
                
                # Extract face region
                face_image = rgb_frame[y1:y2, x1:x2]
                
                # Generate face encoding
                face_encoding = face_encodings(face_image)
                
                if len(face_encoding) == 0:
                    continue
                
                # Compare with known admin faces
                matches = compare_faces(self.admin_encodings, face_encoding[0], tolerance=0.6)
                
                for i, match in enumerate(matches):
                    if match:
                        admin_name = self.admin_names[i]
                        self.logger.info(f"Admin recognized: {admin_name} (confidence: {confidence:.2f})")
                        return True, admin_name, confidence
            
            return False, None, 0.0
            
        except Exception as e:
            self.logger.error(f"Error in face recognition: {e}")
            return False, None, 0.0
    
    def capture_admin_face(self, admin_name: str, num_samples: int = 5) -> bool:
        """
        Capture admin face samples for training
        
        Args:
            admin_name: Name of the admin
            num_samples: Number of face samples to capture
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.logger.error("Failed to open camera")
                return False
            
            self.logger.info(f"Capturing {num_samples} face samples for {admin_name}")
            self.logger.info("Press 'c' to capture, 'q' to quit")
            
            captured_count = 0
            sample_dir = os.path.join(self.admin_faces_dir, admin_name)
            os.makedirs(sample_dir, exist_ok=True)
            
            while captured_count < num_samples:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Display frame
                display_frame = frame.copy()
                cv2.putText(display_frame, f"Captured: {captured_count}/{num_samples}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(display_frame, "Press 'c' to capture, 'q' to quit", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Capture Admin Face', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    # Save captured frame
                    sample_path = os.path.join(sample_dir, f"{admin_name}_{captured_count}.jpg")
                    cv2.imwrite(sample_path, frame)
                    
                    # Add to admin faces
                    if self.add_admin_face(sample_path, admin_name):
                        captured_count += 1
                        self.logger.info(f"Captured sample {captured_count}/{num_samples}")
            
            cap.release()
            cv2.destroyAllWindows()
            
            self.logger.info(f"Successfully captured {captured_count} face samples for {admin_name}")
            return captured_count > 0
            
        except Exception as e:
            self.logger.error(f"Error capturing admin face: {e}")
            return False
    
    def real_time_recognition(self, duration: int = 30) -> bool:
        """
        Perform real-time face recognition for admin authentication
        
        Args:
            duration: Duration in seconds to perform recognition
            
        Returns:
            True if admin face is recognized, False otherwise
        """
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.logger.error("Failed to open camera")
                return False
            
            start_time = time.time()
            self.logger.info(f"Starting real-time admin face recognition for {duration} seconds")
            
            while time.time() - start_time < duration:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Perform face recognition
                is_admin, admin_name, confidence = self.recognize_admin_face(frame)
                
                # Display results
                display_frame = frame.copy()
                if is_admin:
                    cv2.putText(display_frame, f"ADMIN: {admin_name}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(display_frame, f"Confidence: {confidence:.2f}", 
                               (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(display_frame, "No Admin Detected", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                remaining_time = int(duration - (time.time() - start_time))
                cv2.putText(display_frame, f"Time: {remaining_time}s", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Admin Face Recognition', display_frame)
                
                # Check for admin recognition
                if is_admin:
                    self.logger.info(f"Admin {admin_name} recognized! Authentication successful.")
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            self.logger.warning("Admin face recognition timeout - no admin detected")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in real-time recognition: {e}")
            return False

if __name__ == "__main__":
    # Example usage
    face_recognition = AdminFaceRecognition()
    
    # Add a new admin (uncomment to add new admin)
    # face_recognition.capture_admin_face("admin_user")
    
    # Test real-time recognition
    print("Testing admin face recognition...")
    is_authenticated = face_recognition.real_time_recognition(duration=30)
    
    if is_authenticated:
        print("Admin authentication successful!")
    else:
        print("Admin authentication failed!")
