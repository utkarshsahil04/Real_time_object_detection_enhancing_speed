"""
Real-Time Object Detection Using Image Processing in Surveillance Systems
Project ID: BTP2CSE341
Authors: Paridhi Khakolia, Varun, Hardik Bisht, Zayed Alam, Utkarsh Verma
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from collections import defaultdict
from datetime import datetime

class SurveillanceDetector:
    def __init__(self, model_size='n', confidence=0.40, iou=0.45):
        """
        Initialize the surveillance detection system.
        
        Args:
            model_size: 'n' (nano), 's' (small), 'm' (medium) - nano is fastest
            confidence: Detection confidence threshold (0.0-1.0)
            iou: Non-Maximum Suppression IoU threshold
        """
        print(f"[*] Loading YOLOv8{model_size} model...")
        self.model = YOLO(f'yolov8{model_size}.pt')
        self.confidence = confidence
        self.iou = iou
        
        # Hardware optimization for RTX 4060
        import torch
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.half = self.device == 'cuda'  # Use FP16 only on GPU
        print(f"[*] Running on: {self.device} (Half Precision: {self.half})")
        
        # Surveillance-relevant classes
        self.surveillance_classes = {
            0: 'person',
            1: 'bicycle',
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck',
            24: 'backpack',
            26: 'handbag',
            28: 'suitcase',
            39: 'bottle',
            41: 'cup',
            63: 'laptop',
            64: 'mouse',
            65: 'remote',
            66: 'keyboard',
            67: 'cell phone',
            73: 'book',
            74: 'clock',
            75: 'vase',
            76: 'scissors'
        }
        
        # Color map for each class (BGR format for OpenCV)
        self.class_colors = {
            'person': (0, 255, 0),        # Green
            'bicycle': (255, 0, 0),       # Blue
            'car': (0, 165, 255),         # Orange
            'motorcycle': (255, 0, 255),  # Magenta
            'bus': (0, 255, 255),         # Yellow
            'truck': (255, 255, 0),       # Cyan
            'backpack': (128, 0, 128),    # Purple
            'handbag': (128, 128, 0),     # Teal
            'suitcase': (0, 128, 128),    # Dark cyan
            'bottle': (170, 110, 40),
            'cup': (255, 250, 200),
            'laptop': (128, 0, 0),
            'mouse': (170, 255, 195),
            'remote': (128, 128, 0),
            'keyboard': (255, 215, 180),
            'cell phone': (0, 0, 128),
            'book': (128, 128, 128),
            'clock': (255, 255, 255),
            'vase': (0, 0, 0),
            'scissors': (0, 128, 128)
        }
        
        # Detection statistics
        self.detection_counts = defaultdict(int)
        self.frame_count = 0
        self.start_time = time.time()
        
        print("[+] Model loaded successfully!")
    
    def detect_objects(self, frame):
        """
        Run YOLO detection on a frame.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            results: YOLO detection results
            detections: Filtered detections for surveillance
        """
        # Run YOLOv8 inference optimized for hardware
        results = self.model(
            frame, 
            conf=self.confidence, 
            iou=self.iou, 
            verbose=False, 
            device=self.device, 
            half=self.half
        )
        
        # Extract and filter detections
        detections = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                # Filter to surveillance-relevant classes only
                if class_id in self.surveillance_classes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append({
                        'class_id': class_id,
                        'class_name': self.surveillance_classes[class_id],
                        'confidence': confidence,
                        'bbox': (x1, y1, x2, y2)
                    })
                    self.detection_counts[self.surveillance_classes[class_id]] += 1
        
        return results, detections
    
    def annotate_frame(self, frame, detections):
        """
        Draw bounding boxes and labels on frame.
        
        Args:
            frame: Input frame
            detections: List of detected objects
            
        Returns:
            annotated_frame: Frame with annotations
        """
        annotated = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # Get color for this class
            color = self.class_colors.get(class_name, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label
            label = f"{class_name} {confidence:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            
            # Get text size for background
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, thickness
            )
            
            # Draw semi-transparent background for text
            overlay = annotated.copy()
            cv2.rectangle(
                overlay,
                (x1, y1 - text_height - 10),
                (x1 + text_width + 10, y1),
                color,
                -1
            )
            cv2.addWeighted(overlay, 0.7, annotated, 0.3, 0, annotated)
            
            # Draw text
            cv2.putText(
                annotated,
                label,
                (x1 + 5, y1 - 5),
                font,
                font_scale,
                (255, 255, 255),
                thickness
            )
        
        return annotated
    
    def draw_stats(self, frame, fps, detections):
        """
        Draw statistics on frame.
        
        Args:
            frame: Input frame
            fps: Current frames per second
            detections: Current frame detections
            
        Returns:
            frame: Frame with statistics
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # FPS counter
        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (10, 30),
            font,
            1.0,
            (0, 255, 0),
            2
        )
        
        # Detection count
        cv2.putText(
            frame,
            f"Detections: {len(detections)}",
            (10, 65),
            font,
            0.8,
            (0, 255, 0),
            2
        )
        
        # Total statistics
        y_offset = 100
        if self.detection_counts:
            cv2.putText(
                frame,
                "Detection Summary:",
                (10, y_offset),
                font,
                0.7,
                (255, 255, 0),
                2
            )
            y_offset += 30
            
            for class_name, count in self.detection_counts.items():
                text = f"{class_name}: {count}"
                cv2.putText(
                    frame,
                    text,
                    (10, y_offset),
                    font,
                    0.6,
                    (200, 200, 200),
                    1
                )
                y_offset += 25
        
        return frame
    
    def run(self, video_source=0, output_video=None, max_frames=None):
        """
        Main surveillance loop.
        
        Args:
            video_source: 0 for webcam, or path/URL to video
            output_video: Optional path to save output video
            max_frames: Optional limit on number of frames to process
        """
        print(f"[*] Opening video source: {video_source}")
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            print("[!] Failed to open video source!")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"[+] Video properties: {width}x{height} @ {fps} FPS")
        
        # Initialize video writer if output requested
        writer = None
        if output_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
            print(f"[+] Recording to: {output_video}")
        
        frame_times = []
        frame_num = 0
        
        print("[*] Starting detection loop. Press 'Q' to stop...")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[!] Failed to read frame")
                    break
                
                if max_frames and frame_num >= max_frames:
                    break
                
                frame_num += 1
                loop_start = time.time()
                
                # Detect objects
                _, detections = self.detect_objects(frame)
                
                # Annotate frame
                annotated = self.annotate_frame(frame, detections)
                
                # Calculate FPS
                frame_time = time.time() - loop_start
                frame_times.append(frame_time)
                if len(frame_times) > 30:
                    frame_times.pop(0)
                avg_frame_time = np.mean(frame_times)
                current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
                
                # Draw statistics
                annotated = self.draw_stats(annotated, current_fps, detections)
                
                # Save frame if recording
                if writer:
                    writer.write(annotated)
                
                # Display
                cv2.imshow('Real-Time Surveillance Detection', annotated)
                
                # Print per-frame info every 30 frames
                if frame_num % 30 == 0:
                    elapsed = time.time() - self.start_time
                    print(f"[Frame {frame_num}] Time: {elapsed:.1f}s | FPS: {current_fps:.1f} | Detections: {len(detections)}")
                
                # Exit on 'Q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("[*] Stopping detection...")
                    break
        
        except KeyboardInterrupt:
            print("\n[*] Interrupted by user")
        
        finally:
            # Cleanup
            cap.release()
            if writer:
                writer.release()
            cv2.destroyAllWindows()
            
            # Final statistics
            total_time = time.time() - self.start_time
            avg_fps = frame_num / total_time if total_time > 0 else 0
            
            print("\n" + "="*50)
            print("SURVEILLANCE SESSION SUMMARY")
            print("="*50)
            print(f"Total Frames Processed: {frame_num}")
            print(f"Total Time: {total_time:.1f} seconds")
            print(f"Average FPS: {avg_fps:.1f}")
            print(f"\nDetection Summary:")
            for class_name in sorted(self.detection_counts.keys()):
                count = self.detection_counts[class_name]
                print(f"  {class_name}: {count}")
            print("="*50)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Real-Time Object Detection for Surveillance Systems'
    )
    parser.add_argument(
        '--source',
        type=str,
        default='0',
        help='Video source: 0 for webcam, or path/URL to video (default: 0)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='m',
        choices=['n', 's', 'm'],
        help='Model size: n=nano (fastest), s=small, m=medium (default: m, optimized for RTX4060)'
    )
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.40,
        help='Detection confidence threshold (default: 0.40)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Optional output video file path'
    )
    parser.add_argument(
        '--max-frames',
        type=int,
        default=None,
        help='Optional maximum number of frames to process'
    )
    
    args = parser.parse_args()
    
    # Convert source to int if it's a number
    try:
        video_source = int(args.source)
    except ValueError:
        video_source = args.source
    
    # Initialize and run detector
    detector = SurveillanceDetector(
        model_size=args.model,
        confidence=args.confidence
    )
    
    detector.run(
        video_source=video_source,
        output_video=args.output,
        max_frames=args.max_frames
    )


if __name__ == '__main__':
    main()
