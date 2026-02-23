"""
Encapsulates the MediaPipe Hand Landmarker logic for hand tracking and gesture recognition.
"""
import os
import math
import logging
import urllib.request
from urllib.error import URLError
from typing import Optional, Dict, Any

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
PINCH_THRESHOLD = 0.22
DEFAULT_MODEL_PATH = "hand_landmarker.task"

class HandTracker:
    """
    Initializes and manages the MediaPipe Hand Landmarker model to extract
    normalized coordinates and pinch gestures from RGB image frames.
    """

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH) -> None:
        self._ensure_model(model_path)
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def _ensure_model(self, model_path: str) -> None:
        """Downloads the AI model securely, handling potential network failures."""
        if not os.path.exists(model_path):
            logging.info("Downloading Hand Landmarker AI model...")
            try:
                urllib.request.urlretrieve(MODEL_URL, model_path)
                logging.info("Model downloaded successfully.")
            except URLError as e:
                logging.error("Failed to download the model: %s", e)
                raise SystemExit("CRITICAL: Cannot proceed without the tracking model. Check your internet connection.")

    def process_frame(self, image_rgb: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Analyzes an RGB frame to detect hand landmarks and calculate pinch status.
        
        Args:
            image_rgb: A numpy array representing the RGB image frame.
            
        Returns:
            A dictionary containing normalized x/y cursor coordinates, pinch boolean, 
            and raw pixel coordinates for the thumb and index fingers. 
            Returns None if no hand is detected.
        """
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        result = self.detector.detect(mp_image)
        
        if not result.hand_landmarks:
            return None

        landmarks = result.hand_landmarks[0]
        thumb, index = landmarks[4], landmarks[8]
        wrist, knuckle = landmarks[0], landmarks[5]
        
        # Calculate relative pinch ratio based on current hand scale
        pinch_dist = math.hypot(thumb.x - index.x, thumb.y - index.y)
        hand_size = math.hypot(wrist.x - knuckle.x, wrist.y - knuckle.y)
        pinch_ratio = pinch_dist / (hand_size + 1e-6)
        
        logging.debug("Pinch Ratio: %.3f", pinch_ratio)
        
        return {
            'x': (thumb.x + index.x) / 2.0,
            'y': (thumb.y + index.y) / 2.0,
            'is_pinched': pinch_ratio < PINCH_THRESHOLD,
            'thumb_px': (thumb.x, thumb.y),
            'index_px': (index.x, index.y)
        }