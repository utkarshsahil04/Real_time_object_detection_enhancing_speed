"""
Detection Logging and Storage Module
Stores all detections in SQLite database for analysis
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class DetectionLogger:
    def __init__(self, db_path='detections.db'):
        """Initialize database for storing detections."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Detections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                frame_number INTEGER,
                class_name TEXT,
                confidence REAL,
                bbox_x1 INTEGER,
                bbox_y1 INTEGER,
                bbox_x2 INTEGER,
                bbox_y2 INTEGER
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT,
                description TEXT,
                detection_count INTEGER,
                acknowledged BOOLEAN DEFAULT 0
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                total_frames INTEGER,
                average_fps REAL,
                video_source TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_detection(self, frame_number, detections):
        """
        Log detections for a frame.
        
        Args:
            frame_number: Frame sequence number
            detections: List of detection dictionaries
        """
        if not detections:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            cursor.execute('''
                INSERT INTO detections 
                (frame_number, class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                frame_number,
                detection['class_name'],
                detection['confidence'],
                x1, y1, x2, y2
            ))
        
        conn.commit()
        conn.close()
    
    def log_alert(self, alert_type, description, detection_count):
        """
        Log an alert event.
        
        Args:
            alert_type: Type of alert (e.g., 'intrusion', 'crowd')
            description: Alert description
            detection_count: Number of detections that triggered alert
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (alert_type, description, detection_count)
            VALUES (?, ?, ?)
        ''', (alert_type, description, detection_count))
        
        conn.commit()
        conn.close()
    
    def log_session(self, start_time, end_time, total_frames, avg_fps, video_source):
        """
        Log a surveillance session.
        
        Args:
            start_time: Session start timestamp
            end_time: Session end timestamp
            total_frames: Total frames processed
            avg_fps: Average FPS achieved
            video_source: Source of video (webcam/rtsp/file)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions 
            (start_time, end_time, total_frames, average_fps, video_source)
            VALUES (?, ?, ?, ?, ?)
        ''', (start_time, end_time, total_frames, avg_fps, video_source))
        
        conn.commit()
        conn.close()
    
    def get_detections(self, hours=1, class_name=None):
        """
        Retrieve detections from past hours.
        
        Args:
            hours: Number of hours to look back
            class_name: Optional filter by class
            
        Returns:
            List of detection records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM detections 
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        '''
        params = [hours]
        
        if class_name:
            query += ' AND class_name = ?'
            params.append(class_name)
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        detections = cursor.fetchall()
        conn.close()
        
        return detections
    
    def get_stats(self, hours=1):
        """
        Get statistics for past hours.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total detections by class
        cursor.execute('''
            SELECT class_name, COUNT(*) as count
            FROM detections
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            GROUP BY class_name
            ORDER BY count DESC
        ''', [hours])
        
        class_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Total alerts
        cursor.execute('''
            SELECT COUNT(*) FROM alerts
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        ''', [hours])
        
        alert_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'class_detections': class_stats,
            'total_alerts': alert_count,
            'time_period_hours': hours
        }
    
    def cleanup_old_data(self, retention_days=7):
        """
        Delete detections older than retention period.
        
        Args:
            retention_days: Number of days to keep data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM detections
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        ''', [retention_days])
        
        cursor.execute('''
            DELETE FROM alerts
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        ''', [retention_days])
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted


class AlertManager:
    def __init__(self, logger):
        """
        Initialize alert manager.
        
        Args:
            logger: DetectionLogger instance
        """
        self.logger = logger
        self.alert_rules = {
            'crowd': {'min_persons': 5, 'enabled': True},
            'vehicle': {'min_vehicles': 3, 'enabled': True},
            'intrusion': {'min_persons_restricted': 1, 'enabled': True},
        }
    
    def check_alerts(self, detections):
        """
        Check if any alert rules are triggered.
        
        Args:
            detections: List of current frame detections
            
        Returns:
            List of triggered alerts
        """
        alerts = []
        
        if not detections:
            return alerts
        
        # Count by class
        class_counts = {}
        for detection in detections:
            class_name = detection['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        person_count = class_counts.get('person', 0)
        vehicle_count = (
            class_counts.get('car', 0) +
            class_counts.get('motorcycle', 0) +
            class_counts.get('bus', 0) +
            class_counts.get('truck', 0)
        )
        
        # Check crowd detection
        if self.alert_rules['crowd']['enabled'] and person_count >= self.alert_rules['crowd']['min_persons']:
            alerts.append({
                'type': 'crowd',
                'description': f'Crowd detected: {person_count} people',
                'severity': 'medium'
            })
        
        # Check vehicle detection
        if self.alert_rules['vehicle']['enabled'] and vehicle_count >= self.alert_rules['vehicle']['min_vehicles']:
            alerts.append({
                'type': 'vehicle',
                'description': f'Multiple vehicles detected: {vehicle_count} vehicles',
                'severity': 'medium'
            })
        
        # Log triggered alerts
        for alert in alerts:
            self.logger.log_alert(alert['type'], alert['description'], len(detections))
        
        return alerts
    
    def set_rule(self, rule_name, **kwargs):
        """Update an alert rule."""
        if rule_name in self.alert_rules:
            self.alert_rules[rule_name].update(kwargs)
