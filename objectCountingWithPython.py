import cv2
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import argparse

class ObjectCounter:
    def __init__(self):
        self.model = None
        self.classes = None
        self.output_layers = None
        self.colors = None
        self.initialize_model()
        
    def initialize_model(self):
        """Initialize the YOLO model for object detection"""
        # Loading YOLO model and COCO classes
        weights_path = "yolov3.weights"  # download this from the official YOLO website
        config_path = "yolov3.cfg"       # download this
        classes_path = "coco.names"      # download this
        
        # Load COCO class labels
        try:
            with open(classes_path, "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(f"Error: {classes_path} not found. Please download it.")
            self.classes = []
        
        # Generate random colors for each class
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        
        # Load the neural network
        try:
            self.model = cv2.dnn.readNetFromDarknet(config_path, weights_path)
        except cv2.error:
            print(f"Error: Model files not found. Please download {weights_path} and {config_path}")
            return False
            
        # Get output layer names
        layer_names = self.model.getLayerNames()
        try:
            # Different OpenCV versions handle indices differently
            try:
                self.output_layers = [layer_names[i - 1] for i in self.model.getUnconnectedOutLayers()]
            except:
                self.output_layers = [layer_names[i[0] - 1] for i in self.model.getUnconnectedOutLayers()]
        except:
            print("Error determining output layers.")
            return False
            
        return True
    
    def detect_objects(self, image, confidence_threshold=0.5, nms_threshold=0.4):
        """Detect objects in an image using YOLO"""
        if self.model is None:
            print("Model not initialized properly.")
            return [], [], []
            
        height, width, _ = image.shape
        
        # Preprocess image
        blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        
        # Set input and forward pass
        self.model.setInput(blob)
        outs = self.model.forward(self.output_layers)
        
        # Collect detection info
        class_ids = []
        confidences = []
        boxes = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > confidence_threshold:
                    # Object detected, get coordinates
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-maximum suppression to remove overlapping boxes
        indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, nms_threshold)
        
        filtered_boxes = []
        filtered_confidences = []
        filtered_class_ids = []
        
        if len(indices) > 0:
            indices = indices.flatten()
            for i in indices:
                filtered_boxes.append(boxes[i])
                filtered_confidences.append(confidences[i])
                filtered_class_ids.append(class_ids[i])
                
        return filtered_boxes, filtered_confidences, filtered_class_ids
    
    def draw_detections(self, image, boxes, confidences, class_ids):
        """Draw bounding boxes and labels on the image"""
        if not boxes:
            return image
            
        height, width, _ = image.shape
        img_copy = image.copy()
        
        # Count objects by class
        object_counts = Counter([self.classes[class_id] for class_id in class_ids])
        
        # Draw boxes and labels
        for i in range(len(boxes)):
            x, y, w, h = boxes[i]
            
            # Ensure box is within image boundaries
            x = max(0, x)
            y = max(0, y)
            
            # Draw rectangle
            color = self.colors[class_ids[i]]
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{self.classes[class_ids[i]]}: {confidences[i]:.2f}"
            cv2.putText(img_copy, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Add object count at the top
        y_pos = 30
        cv2.putText(img_copy, f"Total objects: {len(boxes)}", (10, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y_pos += 30
        
        # Add count for each class
        for obj_class, count in object_counts.most_common():
            text = f"{obj_class}: {count}"
            cv2.putText(img_copy, text, (10, y_pos), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            y_pos += 30
            
        return img_copy
    
    def count_objects(self, image_path, output_path=None, conf_threshold=0.5, show_image=True):
        """Count objects in an image"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error: Could not read image from {image_path}")
                return None
                
            # Detect objects
            boxes, confidences, class_ids = self.detect_objects(image, conf_threshold)
            
            # Count objects by class
            object_counts = Counter([self.classes[class_id] for class_id in class_ids])
            
            # Draw detections on image
            result_image = self.draw_detections(image, boxes, confidences, class_ids)
            
            # Save result if output path is provided
            if output_path:
                cv2.imwrite(output_path, result_image)
                print(f"Result saved to {output_path}")
            
            # Display result
            if show_image:
                plt.figure(figsize=(12, 8))
                plt.imshow(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
                plt.title(f"Object Detection - Total: {len(boxes)}")
                plt.axis('off')
                plt.show()
            
            # Print summary
            print(f"\nDetected {len(boxes)} objects in the image:")
            for obj_class, count in object_counts.most_common():
                print(f"- {obj_class}: {count}")
                
            return object_counts
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Count objects in an image using YOLO')
    parser.add_argument('image', help='Path to the input image')
    parser.add_argument('--output', '-o', help='Path to save the output image')
    parser.add_argument('--confidence', '-c', type=float, default=0.5,
                        help='Confidence threshold (0-1)')
    parser.add_argument('--no-display', action='store_true',
                        help='Do not display the result image')
    
    args = parser.parse_args()
    
    # Create object counter and process image
    counter = ObjectCounter()
    counter.count_objects(args.image, args.output, args.confidence, not args.no_display)

if __name__ == "__main__":
    main()