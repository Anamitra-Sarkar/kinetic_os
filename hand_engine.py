"""
KINETIC-OS Hand Engine Module
==============================
MediaPipe-based hand landmark detection engine.
Optimized for single-hand tracking with high accuracy.
"""

import mediapipe as mp
import numpy as np
from typing import Optional, NamedTuple, List, Tuple
import config


class HandLandmarks(NamedTuple):
    """Container for hand landmark data."""
    landmarks: List[Tuple[float, float, float]
                    ]  # List of (x, y, z) normalized coords
    handedness: str  # "Left" or "Right"
    raw_landmarks: object  # Original MediaPipe landmarks for drawing


class HandEngine:
    """
    MediaPipe-based hand detection and landmark extraction engine.

    This engine is optimized for:
    - Single hand tracking (max_num_hands=1)
    - High confidence detection and tracking
    - Efficient RGB-only processing
    """

    # MediaPipe hand landmark indices for reference
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20

    def __init__(self):
        """Initialize the MediaPipe Hands solution."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_NUM_HANDS,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        self._last_result = None

    def process_frame(self, rgb_frame: np.ndarray) -> Optional[HandLandmarks]:
        """
        Process an RGB frame and extract hand landmarks.

        Args:
            rgb_frame: Input frame in RGB format (not BGR).

        Returns:
            HandLandmarks object if a hand is detected, None otherwise.

        Note:
            This method only processes the frame for landmark detection.
            It does NOT draw on the original frame for optimization.
        """
        # Process the frame with MediaPipe
        results = self.hands.process(rgb_frame)
        self._last_result = results

        # Check if any hands were detected
        if not results.multi_hand_landmarks:
            return None

        # Extract the first (and only) detected hand
        hand_landmarks = results.multi_hand_landmarks[0]
        handedness = results.multi_handedness[0].classification[0].label

        # Convert landmarks to list of tuples
        landmarks_list = [
            (lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark
        ]

        return HandLandmarks(
            landmarks=landmarks_list,
            handedness=handedness,
            raw_landmarks=hand_landmarks
        )

    def get_landmark(self, hand_data: HandLandmarks,
                     landmark_id: int) -> Tuple[float, float, float]:
        """
        Get a specific landmark from the hand data.

        Args:
            hand_data: HandLandmarks object from process_frame.
            landmark_id: MediaPipe landmark index (0-20).

        Returns:
            Tuple of (x, y, z) normalized coordinates.
        """
        return hand_data.landmarks[landmark_id]

    def get_fingertip(self, hand_data: HandLandmarks,
                      finger: str) -> Tuple[float, float, float]:
        """
        Get the fingertip coordinates for a specific finger.

        Args:
            hand_data: HandLandmarks object from process_frame.
            finger: One of "thumb", "index", "middle", "ring", "pinky".

        Returns:
            Tuple of (x, y, z) normalized coordinates.
        """
        finger_tips = {
            "thumb": self.THUMB_TIP,
            "index": self.INDEX_FINGER_TIP,
            "middle": self.MIDDLE_FINGER_TIP,
            "ring": self.RING_FINGER_TIP,
            "pinky": self.PINKY_TIP
        }
        return self.get_landmark(hand_data, finger_tips[finger.lower()])

    def is_finger_curled(self, hand_data: HandLandmarks, finger: str) -> bool:
        """
        Check if a finger is curled (for fist detection).

        A finger is considered curled if its tip is below its PIP joint
        (closer to the palm) in the y-axis.

        Args:
            hand_data: HandLandmarks object from process_frame.
            finger: One of "index", "middle", "ring", "pinky".

        Returns:
            True if the finger is curled, False otherwise.
        """
        finger_joints = {
            "index": (self.INDEX_FINGER_TIP, self.INDEX_FINGER_PIP, self.INDEX_FINGER_MCP),
            "middle": (self.MIDDLE_FINGER_TIP, self.MIDDLE_FINGER_PIP, self.MIDDLE_FINGER_MCP),
            "ring": (self.RING_FINGER_TIP, self.RING_FINGER_PIP, self.RING_FINGER_MCP),
            "pinky": (self.PINKY_TIP, self.PINKY_PIP, self.PINKY_MCP)
        }

        tip_idx, pip_idx, mcp_idx = finger_joints[finger.lower()]
        tip = hand_data.landmarks[tip_idx]
        pip = hand_data.landmarks[pip_idx]
        mcp = hand_data.landmarks[mcp_idx]

        # Finger is curled if tip is closer to wrist than PIP joint
        # We check both y-coordinate and distance from MCP
        tip_to_mcp = np.sqrt((tip[0] - mcp[0])**2 + (tip[1] - mcp[1])**2)
        pip_to_mcp = np.sqrt((pip[0] - mcp[0])**2 + (pip[1] - mcp[1])**2)

        return tip_to_mcp < pip_to_mcp * 1.2  # Tip should be closer to MCP than PIP

    def is_fist(self, hand_data: HandLandmarks) -> bool:
        """
        Check if the hand is making a fist gesture.

        A fist is detected when all four fingers (index, middle, ring, pinky)
        are curled.

        Args:
            hand_data: HandLandmarks object from process_frame.

        Returns:
            True if the hand is making a fist, False otherwise.
        """
        fingers = ["index", "middle", "ring", "pinky"]
        return all(self.is_finger_curled(hand_data, f) for f in fingers)

    def close(self):
        """Release MediaPipe resources."""
        self.hands.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - release resources."""
        self.close()
