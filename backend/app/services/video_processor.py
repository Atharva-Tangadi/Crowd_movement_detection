import cv2
import time
import asyncio
import base64
import numpy as np
from app.config import settings
from app.detection.detector import PersonDetector
from app.movement.direction import MovementAnalyzer
from app.crowd.density import CrowdAnalyzer
from app.anomaly.detector import AnomalyDetector

class VideoProcessor:
    def __init__(self):
        self.detector = PersonDetector()
        self.movement_analyzer = MovementAnalyzer()
        self.crowd_analyzer = CrowdAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        self.cap = None
        self.is_running = False
        self.stats = {}
        
    def start_camera(self, camera_index=0):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        import os
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, None] if os.name == 'nt' else [None]
        indices = [camera_index, 1, 2] if camera_index == 0 else [camera_index]
        
        opened = False
        for idx in indices:
            for backend in backends:
                try:
                    if backend is not None:
                        cap = cv2.VideoCapture(idx, backend)
                    else:
                        cap = cv2.VideoCapture(idx)
                    if cap.isOpened():
                        ret, _ = cap.read()
                        if ret:
                            self.cap = cap
                            opened = True
                            break
                    cap.release()
                except Exception:
                    pass
            if opened:
                break
                
        if opened:
            self.is_running = True
            return True
        else:
            self.is_running = False
            return False
        
    def start_video(self, video_path):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.cap = cv2.VideoCapture(video_path)
        if self.cap.isOpened():
            self.is_running = True
            return True
        else:
            self.is_running = False
            return False
        
    def stop(self):
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def draw_annotations(self, frame, results, movement_data, crowd_data, active_alert, fps):
        """Draw bounding boxes, IDs, directions, and stats on the frame."""
        annotated_frame = frame.copy()
        
        if results and results.boxes and results.boxes.id is not None:
            boxes = results.boxes.xyxy.cpu().numpy()
            ids = results.boxes.id.int().cpu().numpy()
            
            for box, track_id in zip(boxes, ids):
                x1, y1, x2, y2 = map(int, box)
                
                # Draw Box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Get direction
                direction_info = movement_data['individual'].get(str(track_id), {})
                direction = direction_info.get('direction', 'Unknown')
                
                # Draw ID and Direction
                label = f"ID: {track_id} | {direction}"
                cv2.putText(annotated_frame, label, (x1, max(10, y1 - 10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            
                # Draw Movement Arrow
                dx = direction_info.get('dx', 0)
                dy = direction_info.get('dy', 0)
                if abs(dx) > 0 or abs(dy) > 0:
                    center_x, center_y = int((x1+x2)/2), int((y1+y2)/2)
                    end_x = int(center_x + dx * 2) # Scale for visibility
                    end_y = int(center_y + dy * 2)
                    cv2.arrowedLine(annotated_frame, (center_x, center_y), (end_x, end_y), (255, 0, 0), 2)

        # Draw clean dark HUD overlay box in top-left
        overlay = annotated_frame.copy()
        cv2.rectangle(overlay, (10, 10), (240, 105), (0, 0, 0), -1)
        annotated_frame = cv2.addWeighted(overlay, 0.5, annotated_frame, 0.5, 0)

        # Overlay Stats
        cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.putText(annotated_frame, f"Count: {crowd_data['count']} (Peak: {crowd_data['peak']})", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.putText(annotated_frame, f"Density: {crowd_data['status']}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0) if crowd_data['status'] == "LOW" else (0, 165, 255), 1)
        cv2.putText(annotated_frame, f"Dominant: {movement_data['dominant']}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        
        # Overlay Alert
        if active_alert:
            cv2.putText(annotated_frame, f"ALERT: {active_alert['type']}", (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        return annotated_frame

    def generate_frames(self):
        """Generator for SSE / Multipart response yielding JPEGs."""
        frame_time = 1.0 / settings.target_fps
        
        while self.is_running and self.cap and self.cap.isOpened():
            start_time = time.time()
            
            ret, frame = self.cap.read()
            if not ret:
                # Video ended or error
                self.is_running = False
                self.stats['status'] = 'Stopped'
                break
                
            # Resize for consistent processing
            frame = cv2.resize(frame, (settings.img_size, int(settings.img_size * frame.shape[0] / frame.shape[1])))
            
            # Process Frame
            results = self.detector.track(frame)
            
            # Extract boxes and IDs
            boxes = []
            ids = []
            if results and results.boxes and results.boxes.id is not None:
                boxes = results.boxes.xyxy.cpu().numpy()
                ids = results.boxes.id.int().cpu().numpy()
                
            # Analyze
            movement_data = self.movement_analyzer.analyze_frame(boxes, ids)
            crowd_data = self.crowd_analyzer.analyze(len(ids))
            active_alert = self.anomaly_detector.check_anomalies(crowd_data, movement_data)
            
            # Compute actual FPS
            process_time = time.time() - start_time
            fps = 1.0 / process_time if process_time > 0 else 0
            
            # Annotate
            annotated_frame = self.draw_annotations(frame, results, movement_data, crowd_data, active_alert, fps)
            
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            
            # Update global stats for websocket polling
            self.stats = {
                'crowd': crowd_data,
                'movement': movement_data,
                'alert': active_alert,
                'fps': round(fps, 1),
                'status': 'Running'
            }
            
            # Yield for Multipart HTTP response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Maintain target FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)

processor = VideoProcessor()
