"""
Encapsulates the MediaPipe Face Landmarker logic.
"""
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class GazeTracker:
    def __init__(self, model_path='face_landmarker.task'):
        self._ensure_model(model_path)
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False, # Disabled to save CPU cycles
            output_facial_transformation_matrixes=False,
            num_faces=1
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def _ensure_model(self, model_path):
        """Downloads the AI model if it doesn't exist locally."""
        if not os.path.exists(model_path):
            print("Downloading Face Landmarker AI model...")
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url, model_path)

    def process_frame(self, image_rgb):
        """Analyzes a frame and returns normalized iris coordinates."""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        result = self.detector.detect(mp_image)
        
        if result.face_landmarks:
            landmarks = result.face_landmarks[0]
            # 468 is left iris, 473 is right iris
            left_iris = landmarks[468]
            right_iris = landmarks[473]
            
            return {
                'left': (left_iris.x, left_iris.y),
                'right': (right_iris.x, right_iris.y),
                'confidence': 1.0 # Placeholder for actual blink detection later
            }
        return None