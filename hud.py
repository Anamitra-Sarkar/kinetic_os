"""
KINETIC-OS HUD Module
======================
Cyberpunk-style visual overlay for the Hand-Gesture Interface.
Iron Man inspired heads-up display with neon aesthetics.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import config
from hand_engine import HandLandmarks


class HUD:
    """
    Cyberpunk-style Heads-Up Display for KINETIC-OS.

    Features:
    - Neon green skeleton connecting hand joints
    - Red active nodes on fingertips
    - Status bar with mode and FPS display
    - Fail-safe region indicator
    - Active region boundary visualization
    """

    # Hand connection pairs for skeleton drawing
    HAND_CONNECTIONS = [
        # Thumb
        (0, 1), (1, 2), (2, 3), (3, 4),
        # Index finger
        (0, 5), (5, 6), (6, 7), (7, 8),
        # Middle finger
        (5, 9), (9, 10), (10, 11), (11, 12),
        # Ring finger
        (9, 13), (13, 14), (14, 15), (15, 16),
        # Pinky
        (13, 17), (17, 18), (18, 19), (19, 20),
        # Palm
        (0, 17)
    ]

    # Active nodes (fingertips that trigger actions)
    ACTIVE_NODES = [4, 8, 12]  # Thumb, Index, Middle tips

    def __init__(self, frame_width: int, frame_height: int):
        """
        Initialize the HUD.

        Args:
            frame_width: Width of the video frame in pixels.
            frame_height: Height of the video frame in pixels.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height

        # Pre-calculate fail-safe region coordinates
        self.failsafe_region = (
            0, 0,
            config.FAILSAFE_X_END,
            config.FAILSAFE_Y_END
        )

        # Pre-calculate active region coordinates
        self.active_region = (
            int(config.ACTIVE_REGION_X_START * frame_width),
            int(config.ACTIVE_REGION_Y_START * frame_height),
            int(config.ACTIVE_REGION_X_END * frame_width),
            int(config.ACTIVE_REGION_Y_END * frame_height)
        )

    def draw_skeleton(
            self,
            frame: np.ndarray,
            hand_data: HandLandmarks) -> None:
        """
        Draw neon green skeleton lines connecting hand joints.

        Args:
            frame: Video frame to draw on (modified in place).
            hand_data: HandLandmarks object with landmark coordinates.
        """
        landmarks = hand_data.landmarks

        for connection in self.HAND_CONNECTIONS:
            start_idx, end_idx = connection
            start = landmarks[start_idx]
            end = landmarks[end_idx]

            # Convert normalized coordinates to pixel coordinates
            start_px = (
                int(start[0] * self.frame_width),
                int(start[1] * self.frame_height)
            )
            end_px = (
                int(end[0] * self.frame_width),
                int(end[1] * self.frame_height)
            )

            # Draw neon glow effect (larger line behind)
            cv2.line(frame, start_px, end_px,
                     config.COLOR_BLACK,
                     config.HUD_LINE_THICKNESS + 2)

            # Draw main neon green line
            cv2.line(frame, start_px, end_px,
                     config.COLOR_NEON_GREEN,
                     config.HUD_LINE_THICKNESS)

    def draw_landmarks(
            self,
            frame: np.ndarray,
            hand_data: HandLandmarks) -> None:
        """
        Draw landmark nodes on the hand.

        Args:
            frame: Video frame to draw on (modified in place).
            hand_data: HandLandmarks object with landmark coordinates.
        """
        landmarks = hand_data.landmarks

        for idx, lm in enumerate(landmarks):
            # Convert normalized coordinates to pixel coordinates
            cx = int(lm[0] * self.frame_width)
            cy = int(lm[1] * self.frame_height)

            if idx in self.ACTIVE_NODES:
                # Draw active nodes (fingertips) with red color and larger radius
                # Outer glow
                cv2.circle(frame, (cx, cy),
                           config.HUD_ACTIVE_NODE_RADIUS + 4,
                           config.COLOR_BLACK, -1)
                # Inner filled circle
                cv2.circle(frame, (cx, cy),
                           config.HUD_ACTIVE_NODE_RADIUS,
                           config.COLOR_NEON_RED, -1)
                # Center highlight
                cv2.circle(frame, (cx, cy),
                           config.HUD_ACTIVE_NODE_RADIUS // 2,
                           config.COLOR_WHITE, -1)
            else:
                # Draw regular nodes with green color
                cv2.circle(frame, (cx, cy),
                           config.HUD_NODE_RADIUS,
                           config.COLOR_NEON_GREEN, -1)

    def draw_status_bar(
        self,
        frame: np.ndarray,
        mode: str,
        fps: float,
        handedness: Optional[str] = None
    ) -> None:
        """
        Draw the status bar in the top-left corner.

        Args:
            frame: Video frame to draw on (modified in place).
            mode: Current mode string (ACTIVE, SCROLL, IDLE).
            fps: Current FPS value.
            handedness: Hand type ("Left" or "Right").
        """
        # Draw semi-transparent background
        overlay = frame.copy()
        bar_height = config.HUD_STATUS_BAR_HEIGHT
        cv2.rectangle(overlay, (0, 0), (self.frame_width, bar_height),
                      config.COLOR_BLACK, -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Draw status text
        hand_str = f" | HAND: {handedness}" if handedness else ""
        status_text = f"MODE: {mode} | FPS: {fps:.1f}{hand_str}"

        # Add cyberpunk styling
        cv2.putText(frame, status_text, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, config.HUD_FONT_SCALE,
                    config.COLOR_NEON_CYAN, 2)

        # Draw decorative lines
        cv2.line(frame, (0, bar_height),
                 (self.frame_width, bar_height),
                 config.COLOR_NEON_CYAN, 1)

    def draw_failsafe_region(
            self,
            frame: np.ndarray,
            is_triggered: bool = False) -> None:
        """
        Draw the fail-safe exit region in the top-left corner.

        Args:
            frame: Video frame to draw on (modified in place).
            is_triggered: If True, shows warning state.
        """
        x1, y1, x2, y2 = self.failsafe_region

        # Offset to not overlap with status bar
        y1 = config.HUD_STATUS_BAR_HEIGHT
        y2 = config.HUD_STATUS_BAR_HEIGHT + config.FAILSAFE_Y_END

        color = config.COLOR_NEON_RED if is_triggered else config.COLOR_FAILSAFE_RED

        # Draw the fail-safe region box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Draw X pattern inside
        cv2.line(frame, (x1 + 5, y1 + 5), (x2 - 5, y2 - 5), color, 2)
        cv2.line(frame, (x2 - 5, y1 + 5), (x1 + 5, y2 - 5), color, 2)

        # Add "EXIT" label
        cv2.putText(frame, "EXIT", (x1 + 10, y2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    def draw_active_region(self, frame: np.ndarray) -> None:
        """
        Draw the active tracking region boundary.

        Args:
            frame: Video frame to draw on (modified in place).
        """
        x1, y1, x2, y2 = self.active_region

        # Draw dashed rectangle for active region
        # Top line
        self._draw_dashed_line(
            frame, (x1, y1), (x2, y1), config.COLOR_NEON_PURPLE)
        # Bottom line
        self._draw_dashed_line(
            frame, (x1, y2), (x2, y2), config.COLOR_NEON_PURPLE)
        # Left line
        self._draw_dashed_line(
            frame, (x1, y1), (x1, y2), config.COLOR_NEON_PURPLE)
        # Right line
        self._draw_dashed_line(
            frame, (x2, y1), (x2, y2), config.COLOR_NEON_PURPLE)

        # Draw corner markers
        corner_size = 20
        # Top-left
        cv2.line(frame, (x1, y1), (x1 + corner_size, y1),
                 config.COLOR_NEON_CYAN, 2)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_size),
                 config.COLOR_NEON_CYAN, 2)
        # Top-right
        cv2.line(frame, (x2, y1), (x2 - corner_size, y1),
                 config.COLOR_NEON_CYAN, 2)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_size),
                 config.COLOR_NEON_CYAN, 2)
        # Bottom-left
        cv2.line(frame, (x1, y2), (x1 + corner_size, y2),
                 config.COLOR_NEON_CYAN, 2)
        cv2.line(frame, (x1, y2), (x1, y2 - corner_size),
                 config.COLOR_NEON_CYAN, 2)
        # Bottom-right
        cv2.line(frame, (x2, y2), (x2 - corner_size, y2),
                 config.COLOR_NEON_CYAN, 2)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_size),
                 config.COLOR_NEON_CYAN, 2)

    def _draw_dashed_line(
        self,
        frame: np.ndarray,
        start: Tuple[int, int],
        end: Tuple[int, int],
        color: Tuple[int, int, int],
        dash_length: int = 10
    ) -> None:
        """
        Draw a dashed line between two points.

        Args:
            frame: Video frame to draw on.
            start: Starting point (x, y).
            end: Ending point (x, y).
            color: Line color in BGR.
            dash_length: Length of each dash in pixels.
        """
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = int(np.sqrt(dx * dx + dy * dy))

        if length == 0:
            return

        # Normalize direction
        dx = dx / length
        dy = dy / length

        # Draw dashes
        for i in range(0, length, dash_length * 2):
            p1 = (int(start[0] + i * dx), int(start[1] + i * dy))
            p2 = (int(start[0] + (i + dash_length) * dx),
                  int(start[1] + (i + dash_length) * dy))
            cv2.line(frame, p1, p2, color, 1)

    def draw_click_indicator(
        self,
        frame: np.ndarray,
        click_type: str,
        position: Tuple[int, int]
    ) -> None:
        """
        Draw a visual indicator for click events.

        Args:
            frame: Video frame to draw on (modified in place).
            click_type: Type of click ("LEFT" or "RIGHT").
            position: Position to draw indicator (x, y).
        """
        color = config.COLOR_NEON_CYAN if click_type == "LEFT" else config.COLOR_NEON_PURPLE

        # Draw expanding circle effect
        cv2.circle(frame, position, 30, color, 2)
        cv2.circle(frame, position, 20, color, -1)

        # Add click type label
        cv2.putText(frame, click_type,
                    (position[0] - 20, position[1] + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def draw_scroll_indicator(
            self,
            frame: np.ndarray,
            scroll_delta: int) -> None:
        """
        Draw a visual indicator for scroll mode.

        Args:
            frame: Video frame to draw on (modified in place).
            scroll_delta: Current scroll delta value.
        """
        center_x = self.frame_width // 2
        center_y = self.frame_height // 2

        # Draw scroll mode indicator
        cv2.putText(frame, "SCROLL MODE",
                    (center_x - 80, center_y - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    config.COLOR_NEON_CYAN, 2)

        # Draw direction arrow
        if scroll_delta != 0:
            arrow_color = config.COLOR_NEON_GREEN
            if scroll_delta > 0:
                # Down arrow
                cv2.arrowedLine(frame,
                                (center_x, center_y - 30),
                                (center_x, center_y + 30),
                                arrow_color, 3, tipLength=0.3)
            else:
                # Up arrow
                cv2.arrowedLine(frame,
                                (center_x, center_y + 30),
                                (center_x, center_y - 30),
                                arrow_color, 3, tipLength=0.3)

    def draw_gesture_distance(
        self,
        frame: np.ndarray,
        point1: Tuple[int, int],
        point2: Tuple[int, int],
        distance: float,
        threshold: float
    ) -> None:
        """
        Draw a line between two points showing gesture distance.

        Args:
            frame: Video frame to draw on (modified in place).
            point1: First point (x, y).
            point2: Second point (x, y).
            distance: Current distance value.
            threshold: Threshold for activation.
        """
        # Color based on proximity to threshold
        if distance < threshold:
            color = config.COLOR_NEON_RED
        elif distance < threshold * 1.5:
            color = config.COLOR_NEON_CYAN
        else:
            color = config.COLOR_NEON_GREEN

        cv2.line(frame, point1, point2, color, 2)

    def render(
        self,
        frame: np.ndarray,
        hand_data: Optional[HandLandmarks],
        mode: str,
        fps: float,
        is_failsafe: bool = False,
        click_info: Optional[Tuple[str, Tuple[int, int]]] = None,
        scroll_delta: int = 0
    ) -> np.ndarray:
        """
        Render the complete HUD on the frame.

        Args:
            frame: Video frame to draw on.
            hand_data: HandLandmarks object (or None if no hand detected).
            mode: Current mode string.
            fps: Current FPS value.
            is_failsafe: True if failsafe region is triggered.
            click_info: Optional tuple of (click_type, position) for click indicator.
            scroll_delta: Scroll delta for scroll indicator.

        Returns:
            Frame with HUD overlay.
        """
        # Make a copy to avoid modifying original
        display_frame = frame.copy()

        # Draw active region boundary
        self.draw_active_region(display_frame)

        # Draw fail-safe region
        self.draw_failsafe_region(display_frame, is_failsafe)

        # Draw hand visualization if detected
        if hand_data is not None:
            self.draw_skeleton(display_frame, hand_data)
            self.draw_landmarks(display_frame, hand_data)

        # Draw mode-specific indicators
        if mode == config.MODE_SCROLL and scroll_delta != 0:
            self.draw_scroll_indicator(display_frame, scroll_delta)

        if click_info is not None:
            click_type, position = click_info
            self.draw_click_indicator(display_frame, click_type, position)

        # Draw status bar (on top of everything)
        handedness = hand_data.handedness if hand_data else None
        self.draw_status_bar(display_frame, mode, fps, handedness)

        return display_frame
