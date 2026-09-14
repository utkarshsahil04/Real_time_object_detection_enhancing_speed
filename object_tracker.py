"""
Object Tracking Module
Tracks detected objects across frames using centroid tracking
"""

import numpy as np
from collections import defaultdict
from scipy.spatial import distance as dist


class CentroidTracker:
    def __init__(self, max_disappeared=50):
        """
        Initialize centroid tracker.
        
        Args:
            max_disappeared: Max frames an object can disappear before untracking
        """
        self.next_object_id = 0
        self.objects = {}  # {id: centroid}
        self.disappeared = defaultdict(int)
        self.max_disappeared = max_disappeared
        self.object_history = defaultdict(list)  # Track centroid history
    
    def register(self, centroid):
        """Register a new object."""
        self.objects[self.next_object_id] = centroid
        self.object_history[self.next_object_id] = [centroid]
        self.next_object_id += 1
    
    def deregister(self, object_id):
        """Deregister an object by ID."""
        del self.objects[object_id]
        del self.disappeared[object_id]
        del self.object_history[object_id]
    
    def update(self, detections):
        """
        Update tracked objects with new detections.
        
        Args:
            detections: List of detections, each with bbox as (x1, y1, x2, y2)
            
        Returns:
            Dictionary of {object_id: centroid}
        """
        if len(detections) == 0:
            # Mark all objects as disappeared
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            
            return self.objects
        
        # Compute centroids of new detections
        input_centroids = []
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            input_centroids.append((cx, cy))
        
        input_centroids = np.array(input_centroids)
        
        # If no tracked objects, register all new detections
        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i])
        else:
            # Match existing objects to new centroids
            object_ids = list(self.objects.keys())
            object_centroids = np.array([self.objects[oid] for oid in object_ids])
            
            # Compute distance between each pair
            D = dist.cdist(object_centroids, input_centroids)
            
            # Find matches (greedy approach)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                if D[row, col] > 50:  # Distance threshold
                    continue
                
                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.object_history[object_id].append(input_centroids[col])
                self.disappeared[object_id] = 0
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Register new objects
            unused_rows = set(range(len(object_centroids))) - used_rows
            for row in unused_rows:
                self.register(input_centroids[row])
            
            # Deregister objects
            for row in set(range(len(object_centroids))) - used_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
        
        return self.objects
    
    def get_tracking_info(self):
        """Get current tracking info."""
        return {
            'tracked_objects': len(self.objects),
            'object_ids': list(self.objects.keys()),
            'centroids': list(self.objects.values())
        }


class BehaviorAnalyzer:
    """Analyze object behavior patterns."""
    
    def __init__(self, frame_width, frame_height):
        """
        Initialize behavior analyzer.
        
        Args:
            frame_width: Frame width
            frame_height: Frame height
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.loitering_threshold = 60  # frames
        self.loitering_objects = defaultdict(int)
    
    def check_loitering(self, object_id, centroid, history, min_distance=10):
        """
        Check if object is loitering (stationary).
        
        Args:
            object_id: Object ID
            centroid: Current centroid
            history: List of past centroids
            min_distance: Min movement to not count as loitering
            
        Returns:
            Boolean indicating if object is loitering
        """
        if len(history) < 30:
            return False
        
        # Check movement in last 30 frames
        recent_history = history[-30:]
        movements = [
            np.sqrt((recent_history[i+1][0] - recent_history[i][0])**2 +
                   (recent_history[i+1][1] - recent_history[i][1])**2)
            for i in range(len(recent_history) - 1)
        ]
        
        avg_movement = np.mean(movements)
        
        if avg_movement < min_distance:
            self.loitering_objects[object_id] += 1
        else:
            self.loitering_objects[object_id] = 0
        
        return self.loitering_objects[object_id] > self.loitering_threshold
    
    def check_boundary_crossing(self, object_id, old_centroid, new_centroid, boundary_y):
        """
        Check if object crosses a virtual line.
        
        Args:
            object_id: Object ID
            old_centroid: Previous centroid
            new_centroid: Current centroid
            boundary_y: Y-coordinate of boundary line
            
        Returns:
            'crossed' if crossed, 'approaching' if near, None otherwise
        """
        old_y = old_centroid[1]
        new_y = new_centroid[1]
        
        # Check if crossed
        if (old_y < boundary_y <= new_y) or (old_y > boundary_y >= new_y):
            return 'crossed'
        
        # Check if approaching
        if abs(new_y - boundary_y) < 20:
            return 'approaching'
        
        return None
    
    def check_speed(self, object_id, old_centroid, new_centroid, fps=30, threshold_kmh=20):
        """
        Check if object is moving too fast (potential vehicle).
        
        Args:
            object_id: Object ID
            old_centroid: Previous centroid
            new_centroid: Current centroid
            fps: Frames per second
            threshold_kmh: Speed threshold in km/h
            
        Returns:
            Speed in pixels/frame or None
        """
        pixel_distance = np.sqrt(
            (new_centroid[0] - old_centroid[0])**2 +
            (new_centroid[1] - old_centroid[1])**2
        )
        
        return pixel_distance


class EventDetector:
    """Detect surveillance events based on object behavior."""
    
    def __init__(self, frame_width, frame_height):
        """Initialize event detector."""
        self.analyzer = BehaviorAnalyzer(frame_width, frame_height)
        self.events = []
    
    def detect_events(self, tracker, detections):
        """
        Detect events based on current state.
        
        Args:
            tracker: CentroidTracker instance
            detections: Current frame detections
            
        Returns:
            List of detected events
        """
        events = []
        
        tracking_info = tracker.get_tracking_info()
        
        for obj_id in tracking_info['object_ids']:
            if obj_id not in tracker.object_history:
                continue
            
            history = tracker.object_history[obj_id]
            
            # Check loitering
            if tracker.objects[obj_id] is not None:
                if self.analyzer.check_loitering(
                    obj_id,
                    tracker.objects[obj_id],
                    history
                ):
                    events.append({
                        'type': 'loitering',
                        'object_id': obj_id,
                        'severity': 'medium'
                    })
        
        self.events = events
        return events
