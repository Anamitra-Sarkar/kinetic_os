"""
KINETIC-OS Cursor Math Module
==============================
Mathematical operations for smooth cursor control.
Implements Exponential Moving Average (EMA) filtering
and coordinate mapping with active region support.
"""

import math
from typing import Tuple, Optional
import config


class CursorMath:
    """
    Handles the mathematics for smooth cursor movement.

    Key features:
    - Exponential Moving Average (EMA) smoothing for butter-smooth cursor
    - Active region mapping (center 60% of camera to full screen)
    - Euclidean distance calculations for gesture detection
    """

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the cursor math engine.

        Args:
            screen_width: Width of the screen in pixels.
            screen_height: Height of the screen in pixels.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Previous smoothed position for EMA filter
        self._prev_x: Optional[float] = None
        self._prev_y: Optional[float] = None

        # Previous raw Y position for scroll calculation
        self._prev_scroll_y: Optional[float] = None

        # Active region boundaries (normalized 0-1)
        self.active_x_start = config.ACTIVE_REGION_X_START
        self.active_x_end = config.ACTIVE_REGION_X_END
        self.active_y_start = config.ACTIVE_REGION_Y_START
        self.active_y_end = config.ACTIVE_REGION_Y_END

    def smooth_position(self, raw_x: float,
                        raw_y: float) -> Tuple[float, float]:
        """
        Apply Exponential Moving Average (EMA) smoothing to cursor position.

        Formula: current = prev + (raw - prev) / smoothing_factor

        Args:
            raw_x: Raw X coordinate (normalized 0-1).
            raw_y: Raw Y coordinate (normalized 0-1).

        Returns:
            Tuple of (smoothed_x, smoothed_y) coordinates.
        """
        if self._prev_x is None or self._prev_y is None:
            # First frame - initialize with raw values
            self._prev_x = raw_x
            self._prev_y = raw_y
            return raw_x, raw_y

        # Apply EMA smoothing
        smoothing = config.SMOOTHING_FACTOR
        smoothed_x = self._prev_x + (raw_x - self._prev_x) / smoothing
        smoothed_y = self._prev_y + (raw_y - self._prev_y) / smoothing

        # Update previous values
        self._prev_x = smoothed_x
        self._prev_y = smoothed_y

        return smoothed_x, smoothed_y

    def map_to_screen(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        """
        Map normalized coordinates from active region to screen coordinates.

        This maps the center 60% of the camera view to 100% of the screen,
        reducing the physical movement needed to traverse the entire screen.

        Args:
            norm_x: Normalized X coordinate (0-1).
            norm_y: Normalized Y coordinate (0-1).

        Returns:
            Tuple of (screen_x, screen_y) in pixels.
        """
        # Clamp to active region boundaries
        clamped_x = max(self.active_x_start, min(self.active_x_end, norm_x))
        clamped_y = max(self.active_y_start, min(self.active_y_end, norm_y))

        # Map from active region to 0-1 range
        active_width = self.active_x_end - self.active_x_start
        active_height = self.active_y_end - self.active_y_start

        mapped_x = (clamped_x - self.active_x_start) / active_width
        mapped_y = (clamped_y - self.active_y_start) / active_height

        # Flip X axis (mirror mode - more intuitive control)
        mapped_x = 1.0 - mapped_x

        # Convert to screen coordinates
        screen_x = int(mapped_x * self.screen_width)
        screen_y = int(mapped_y * self.screen_height)

        # Ensure within screen bounds
        screen_x = max(0, min(self.screen_width - 1, screen_x))
        screen_y = max(0, min(self.screen_height - 1, screen_y))

        return screen_x, screen_y

    @staticmethod
    def euclidean_distance(
        point1: Tuple[float, float, float],
        point2: Tuple[float, float, float]
    ) -> float:
        """
        Calculate the 2D Euclidean distance between two landmark points.

        Uses only X and Y coordinates (ignores Z depth).

        Args:
            point1: First point as (x, y, z) tuple.
            point2: Second point as (x, y, z) tuple.

        Returns:
            Euclidean distance between the points.
        """
        dx = point1[0] - point2[0]
        dy = point1[1] - point2[1]
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def is_click(
        thumb_tip: Tuple[float, float, float],
        finger_tip: Tuple[float, float, float]
    ) -> bool:
        """
        Determine if a click gesture is being made.

        A click is detected when the distance between thumb and finger
        is less than the configured threshold.

        Args:
            thumb_tip: Thumb tip coordinates (x, y, z).
            finger_tip: Target finger tip coordinates (x, y, z).

        Returns:
            True if click detected, False otherwise.
        """
        distance = CursorMath.euclidean_distance(thumb_tip, finger_tip)
        return distance < config.CLICK_THRESHOLD

    def calculate_scroll_delta(self, current_y: float) -> int:
        """
        Calculate scroll delta from vertical hand movement.

        Args:
            current_y: Current Y coordinate (normalized 0-1).

        Returns:
            Scroll delta in pixels (positive = scroll down, negative = scroll up).
        """
        if self._prev_scroll_y is None:
            self._prev_scroll_y = current_y
            return 0

        delta = (current_y - self._prev_scroll_y) * \
            config.SCROLL_SENSITIVITY * 100
        self._prev_scroll_y = current_y

        return int(delta)

    def reset_scroll_reference(self):
        """Reset the scroll reference point (call when entering scroll mode)."""
        self._prev_scroll_y = None

    def is_in_failsafe_region(self, screen_x: int, screen_y: int) -> bool:
        """
        Check if the cursor is in the fail-safe exit region.

        Args:
            screen_x: Screen X coordinate in pixels.
            screen_y: Screen Y coordinate in pixels.

        Returns:
            True if cursor is in fail-safe region (top-left corner).
        """
        return (screen_x < config.FAILSAFE_X_END
                and screen_y < config.FAILSAFE_Y_END)

    def reset_smoothing(self):
        """Reset the smoothing filter (call when hand is lost)."""
        self._prev_x = None
        self._prev_y = None


class FPSCounter:
    """Simple FPS counter for performance monitoring."""

    def __init__(self, sample_size: int = 30):
        """
        Initialize the FPS counter.

        Args:
            sample_size: Number of frames to average over.
        """
        self._times: list = []
        self._sample_size = sample_size
        self._last_time: Optional[float] = None

    def tick(self, current_time: float) -> float:
        """
        Record a frame and calculate FPS.

        Args:
            current_time: Current timestamp in seconds.

        Returns:
            Current FPS (averaged over sample_size frames).
        """
        if self._last_time is not None:
            delta = current_time - self._last_time
            if delta > 0:
                self._times.append(delta)
                if len(self._times) > self._sample_size:
                    self._times.pop(0)

        self._last_time = current_time

        if not self._times:
            return 0.0

        avg_delta = sum(self._times) / len(self._times)
        return 1.0 / avg_delta if avg_delta > 0 else 0.0
