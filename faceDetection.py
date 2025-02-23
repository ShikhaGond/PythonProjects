import cv2
import numpy as np
from pathlib import Path
import logging
import dlib
import time
import pickle
from deepface import DeepFace
from concurrent.futures import ThreadPoolExecutor
import face_recognition
import os
from tqdm import tqdm
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetectorType(Enum):
    FRONTAL_FACE = "haarcascade_frontalface_default.xml"
    PROFILE_FACE = "haarcascade_profileface.xml"
    EYES = "haarcascade_eye.xml"
    SMILE = "haarcascade_smile.xml"

class FaceRecognitionSystem:
    def __init__(self, known_faces_dir="known_faces", encodings_path="face_encodings.pkl"):
        """
        Initialize the face recognition system
        
        Args:
            known_faces_dir (str): Directory containing known face images
            encodings_path (str): Path to save/load face encodings
        """
        self.known_faces_dir = Path(known_faces_dir)
        self.encodings_path = Path(encodings_path)
        self.known_face_encodings = []
        self.known_face_names = []
        
        self.load_or_create_encodings()

    def load_or_create_encodings(self):
        """Load existing face encodings or create new ones from known_faces directory"""
        if self.encodings_path.exists():
            logger.info("Loading existing face encodings...")
            with open(self.encodings_path, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
        else:
            logger.info("Creating new face encodings...")
            self.create_encodings()

    def create_encodings(self):
        """Create face encodings from images in known_faces directory"""
        if not self.known_faces_dir.exists():
            logger.warning(f"Known faces directory not found: {self.known_faces_dir}")
            return

        for person_dir in self.known_faces_dir.iterdir():
            if person_dir.is_dir():
                person_name = person_dir.name
                logger.info(f"Processing images for {person_name}")
                
                for image_path in person_dir.glob("*.jpg"):
                    try:
                        image = face_recognition.load_image_file(str(image_path))
                        encodings = face_recognition.face_encodings(image)
                        
                        if encodings:
                            self.known_face_encodings.append(encodings[0])
                            self.known_face_names.append(person_name)
                    except Exception as e:
                        logger.error(f"Error processing {image_path}: {e}")

        with open(self.encodings_path, 'wb') as f:
            pickle.dump({
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }, f)

    def identify_face(self, face_encoding):
        """
        Identify a face using stored encodings
        
        Args:
            face_encoding: Face encoding to identify
            
        Returns:
            str: Name of identified person or "Unknown"
        """
        if not self.known_face_encodings:
            return "Unknown"

        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
        if True in matches:
            first_match_index = matches.index(True)
            return self.known_face_names[first_match_index]
        return "Unknown"

class EnhancedFaceDetector:
    def __init__(self, detector_types=None, enable_landmarks=False, enable_recognition=False):
        """
        Initialize the enhanced face detector
        
        Args:
            detector_types (list): List of DetectorType enums
            enable_landmarks (bool): Enable facial landmark detection
            enable_recognition (bool): Enable face recognition
        """
        self.detectors = {}
        self.enable_landmarks = enable_landmarks
        self.enable_recognition = enable_recognition
        
        if not detector_types:
            detector_types = [DetectorType.FRONTAL_FACE]
        
        for detector_type in detector_types:
            cascade_path = cv2.data.haarcascades + detector_type.value
            detector = cv2.CascadeClassifier(cascade_path)
            if detector.empty():
                raise ValueError(f"Error loading cascade classifier: {detector_type.value}")
            self.detectors[detector_type] = detector

        if enable_landmarks:
            self.initialize_landmark_detector()

        if enable_recognition:
            self.face_recognition_system = FaceRecognitionSystem()

    def initialize_landmark_detector(self):
        """Initialize the facial landmark detector"""
        try:
            self.landmark_detector = dlib.get_frontal_face_detector()
            predictor_path = "shape_predictor_68_face_landmarks.dat"
            if not Path(predictor_path).exists():
                raise FileNotFoundError(f"Landmark predictor file not found: {predictor_path}")
            self.landmark_predictor = dlib.shape_predictor(predictor_path)
        except Exception as e:
            logger.error(f"Error initializing landmark detector: {e}")
            self.enable_landmarks = False

    def detect_faces(self, image):
        """
        Detect faces and their features
        
        Args:
            image: NumPy array of the image
            
        Returns:
            dict: Dictionary containing all detections and analysis
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            results = {
                'detections': {},
                'emotions': [],
                'identities': [],
                'landmarks': []
            }
            
            for detector_type, detector in self.detectors.items():
                features = detector.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                results['detections'][detector_type] = features

                if detector_type == DetectorType.FRONTAL_FACE and len(features) > 0:
                    for (x, y, w, h) in features:
                        face_region = image[y:y+h, x:x+w]
                        
                        try:
                            emotion = DeepFace.analyze(
                                face_region,
                                actions=['emotion'],
                                enforce_detection=False
                            )
                            results['emotions'].append(emotion[0]['dominant_emotion'])
                        except:
                            results['emotions'].append(None)

                        if self.enable_recognition:
                            try:
                                face_encoding = face_recognition.face_encodings(face_region)[0]
                                identity = self.face_recognition_system.identify_face(face_encoding)
                                results['identities'].append(identity)
                            except:
                                results['identities'].append("Unknown")

                        if self.enable_landmarks:
                            try:
                                landmarks = self.detect_landmarks(image, (x, y, w, h))
                                results['landmarks'].append(landmarks)
                            except:
                                results['landmarks'].append(None)

            return results
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return None

    def detect_landmarks(self, image, face_rect):
        """Detect facial landmarks for a given face"""
        x, y, w, h = face_rect
        dlib_rect = dlib.rectangle(x, y, x + w, y + h)
        shape = self.landmark_predictor(image, dlib_rect)
        return [(p.x, p.y) for p in shape.parts()]

    def draw_results(self, image, results):
        """Draw all detection results on the image"""
        try:
            image_copy = image.copy()
            
            if not results:
                return image_copy

            frontal_faces = results['detections'].get(DetectorType.FRONTAL_FACE, [])
            for idx, (x, y, w, h) in enumerate(frontal_faces):
                cv2.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)

                if results['identities'] and len(results['identities']) > idx:
                    identity = results['identities'][idx]
                    cv2.putText(image_copy, identity, (x, y - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                if results['emotions'] and len(results['emotions']) > idx:
                    emotion = results['emotions'][idx]
                    if emotion:
                        cv2.putText(image_copy, emotion, (x, y + h + 20),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                if results['landmarks'] and len(results['landmarks']) > idx:
                    landmarks = results['landmarks'][idx]
                    if landmarks:
                        for (px, py) in landmarks:
                            cv2.circle(image_copy, (px, py), 1, (0, 255, 255), -1)

            for detector_type, features in results['detections'].items():
                if detector_type != DetectorType.FRONTAL_FACE:
                    color = (255, 0, 0) if detector_type == DetectorType.PROFILE_FACE else (0, 0, 255)
                    for (x, y, w, h) in features:
                        cv2.rectangle(image_copy, (x, y), (x + w, y + h), color, 2)

            return image_copy
        except Exception as e:
            logger.error(f"Error drawing results: {e}")
            return image

class BatchProcessor:
    def __init__(self, detector):
        """
        Initialize the batch processor
        
        Args:
            detector: EnhancedFaceDetector instance
        """
        self.detector = detector

    def process_image(self, image_path):
        """Process a single image"""
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")

            results = self.detector.detect_faces(image)
            processed_image = self.detector.draw_results(image, results)
            
            return {
                'path': image_path,
                'results': results,
                'processed_image': processed_image
            }
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            return None

    def process_batch(self, input_dir, output_dir, max_workers=4):
        """
        Process a batch of images
        
        Args:
            input_dir (str): Directory containing input images
            output_dir (str): Directory to save processed images
            max_workers (int): Maximum number of concurrent workers
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_files = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))
        
        if not image_files:
            logger.warning(f"No images found in {input_dir}")
            return

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for image_file in image_files:
                future = executor.submit(self.process_image, image_file)
                futures.append(future)

            for future in tqdm(futures, desc="Processing images"):
                try:
                    result = future.result()
                    if result:
                        output_file = output_path / f"processed_{result['path'].name}"
                        cv2.imwrite(str(output_file), result['processed_image'])
                except Exception as e:
                    logger.error(f"Error processing batch: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Face Detection and Recognition System')
    parser.add_argument('--input', type=str, required=True,
                      help='Input image/video file or directory for batch processing')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--batch', action='store_true',
                      help='Enable batch processing mode')
    parser.add_argument('--enable-landmarks', action='store_true',
                      help='Enable facial landmark detection')
    parser.add_argument('--enable-recognition', action='store_true',
                      help='Enable face recognition')
    parser.add_argument('--detectors', nargs='+',
                      choices=[d.name for d in DetectorType],
                      default=['FRONTAL_FACE'],
                      help='Detector types to use')
    
    args = parser.parse_args()
    
    detector_types = [DetectorType[d] for d in args.detectors]
    
    detector = EnhancedFaceDetector(
        detector_types=detector_types,
        enable_landmarks=args.enable_landmarks,
        enable_recognition=args.enable_recognition
    )
    
    if args.batch:
        if not args.output:
            parser.error("--output directory is required for batch processing")
        
        processor = BatchProcessor(detector)
        processor.process_batch(args.input, args.output)
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            parser.error(f"Input file not found: {args.input}")
        
        if input_path.suffix.lower() in ['.jpg', '.png', '.jpeg']:
            image = cv2.imread(str(input_path))
            results = detector.detect_faces(image)
            processed_image = detector.draw_results(image, results)
            
            if args.output:
                cv2.imwrite(args.output, processed_image)
            else:
                cv2.imshow('Results', processed_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        else:
            
            cap = cv2.VideoCapture(str(input_path))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                results = detector.detect_faces(frame)
                processed_frame = detector.draw_results(frame, results)
                
                cv2.imshow('Results', processed_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
