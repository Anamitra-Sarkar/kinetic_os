#!/usr/bin/env python3
"""
KINETIC-OS Main Entry Point
============================
Contactless Hand-Gesture Interface for Linux OS.
Production-grade, butter-smooth cursor control.

Usage:
    python main.py

Controls:
    - Move: Point with index finger (Landmark 8)
    - Left Click: Touch thumb tip to index tip
    - Right Click: Touch thumb tip to middle finger tip
    - Scroll: Make a fist and move up/down
    - Exit: Move hand to top-left fail-safe region OR press 'q'
"""

import sys
import time
import cv2

try:
    import pyautogui
except ImportError:
    print("Error: pyautogui is required. Install with: pip install pyautogui")
    sys.exit(1)

import config
from hand_engine import HandEngine
from cursor_math import CursorMath, FPSCounter
from hud import HUD


class KineticOS:
    """
    Main KINETIC-OS application class.

    Orchestrates hand tracking, cursor control, and visual feedback.
    """

    def __init__(self):
        """Initialize KINETIC-OS components."""
        # Disable PyAutoGUI fail-safe to prevent conflicts with our own
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0  # Remove delay between actions

        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"[KINETIC-OS] Screen: {self.screen_width}x{self.screen_height}")

        # Initialize camera
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Failed to open camera at index {
                    config.CAMERA_INDEX}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)

        # Get actual frame dimensions
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"[KINETIC-OS] Camera: {self.frame_width}x{self.frame_height}")

        # Initialize modules
        self.hand_engine = HandEngine()
        self.cursor_math = CursorMath(self.screen_width, self.screen_height)
        self.hud = HUD(self.frame_width, self.frame_height)
        self.fps_counter = FPSCounter()

        # State tracking
        self.current_mode = config.MODE_IDLE
        self.last_left_click_time = 0
        self.last_right_click_time = 0
        self.last_scroll_time = 0
        self.is_left_clicking = False
        self.is_right_clicking = False
        self.is_scrolling = False
        self.click_indicator = None
        self.click_indicator_time = 0

        print("[KINETIC-OS] Initialization complete. Starting...")

    def _check_left_click(self, hand_data) -> bool:
        """Check for left click gesture (thumb to index)."""
        thumb_tip = self.hand_engine.get_fingertip(hand_data, "thumb")
        index_tip = self.hand_engine.get_fingertip(hand_data, "index")
        return self.cursor_math.is_click(thumb_tip, index_tip)

    def _check_right_click(self, hand_data) -> bool:
        """Check for right click gesture (thumb to middle)."""
        thumb_tip = self.hand_engine.get_fingertip(hand_data, "thumb")
        middle_tip = self.hand_engine.get_fingertip(hand_data, "middle")
        return self.cursor_math.is_click(thumb_tip, middle_tip)

    def _process_gestures(self, hand_data, current_time: float) -> int:
        """
        Process hand gestures and execute corresponding actions.

        Args:
            hand_data: HandLandmarks object.
            current_time: Current timestamp.

        Returns:
            Scroll delta (0 if not scrolling).
        """
        scroll_delta = 0

        # Get index finger position for cursor control
        index_tip = self.hand_engine.get_fingertip(hand_data, "index")

        # Apply smoothing
        smooth_x, smooth_y = self.cursor_math.smooth_position(
            index_tip[0], index_tip[1])

        # Map to screen coordinates
        screen_x, screen_y = self.cursor_math.map_to_screen(smooth_x, smooth_y)

        # Check for fail-safe region
        if self.cursor_math.is_in_failsafe_region(screen_x, screen_y):
            print("\n[KINETIC-OS] Fail-safe triggered! Exiting...")
            return -999  # Special value to indicate exit

        # Check for fist (scroll mode)
        if self.hand_engine.is_fist(hand_data):
            self.current_mode = config.MODE_SCROLL

            if not self.is_scrolling:
                self.is_scrolling = True
                self.cursor_math.reset_scroll_reference()

            # Calculate scroll delta from Y movement
            wrist = self.hand_engine.get_landmark(
                hand_data, self.hand_engine.WRIST)
            scroll_delta = self.cursor_math.calculate_scroll_delta(wrist[1])

            # Execute scroll with debounce
            debounce_ok = (current_time - self.last_scroll_time) > config.SCROLL_DEBOUNCE_TIME
            if abs(scroll_delta) > 0 and debounce_ok:
                # Negative because Y is inverted
                pyautogui.scroll(-scroll_delta)
                self.last_scroll_time = current_time
        else:
            self.is_scrolling = False
            self.current_mode = config.MODE_ACTIVE

            # Move cursor
            pyautogui.moveTo(screen_x, screen_y)

            # Check for left click
            is_left_clicking = self._check_left_click(hand_data)
            if is_left_clicking and not self.is_left_clicking:
                elapsed = current_time - self.last_left_click_time
                if elapsed > config.CLICK_DEBOUNCE_TIME:
                    pyautogui.click(button='left')
                    self.last_left_click_time = current_time
                    self.click_indicator = ("LEFT", (screen_x, screen_y))
                    self.click_indicator_time = current_time
            self.is_left_clicking = is_left_clicking

            # Check for right click
            is_right_clicking = self._check_right_click(hand_data)
            if is_right_clicking and not self.is_right_clicking:
                elapsed = current_time - self.last_right_click_time
                if elapsed > config.CLICK_DEBOUNCE_TIME:
                    pyautogui.click(button='right')
                    self.last_right_click_time = current_time
                    self.click_indicator = ("RIGHT", (screen_x, screen_y))
                    self.click_indicator_time = current_time
            self.is_right_clicking = is_right_clicking

        return scroll_delta

    def run(self):
        """Main application loop."""
        print("[KINETIC-OS] Running... Press 'q' to quit or use fail-safe region.")

        try:
            while True:
                current_time = time.time()

                # Capture frame
                ret, frame = self.cap.read()
                if not ret:
                    print("[KINETIC-OS] Failed to capture frame")
                    continue

                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)

                # Convert BGR to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process frame for hand detection
                hand_data = self.hand_engine.process_frame(rgb_frame)

                # Calculate FPS
                fps = self.fps_counter.tick(current_time)

                # Initialize variables
                scroll_delta = 0
                is_failsafe = False

                if hand_data is not None:
                    # Process gestures
                    result = self._process_gestures(hand_data, current_time)

                    if result == -999:  # Fail-safe exit
                        is_failsafe = True
                        # Render one last frame showing fail-safe triggered
                        display_frame = self.hud.render(
                            frame, hand_data, "EXIT",
                            fps, is_failsafe=True
                        )
                        cv2.imshow("KINETIC-OS", display_frame)
                        cv2.waitKey(500)
                        break

                    scroll_delta = result
                else:
                    # No hand detected
                    self.current_mode = config.MODE_IDLE
                    self.cursor_math.reset_smoothing()
                    self.is_left_clicking = False
                    self.is_right_clicking = False
                    self.is_scrolling = False

                # Clear click indicator after 0.3 seconds
                if self.click_indicator and (
                        current_time - self.click_indicator_time) > 0.3:
                    self.click_indicator = None

                # Render HUD
                display_frame = self.hud.render(
                    frame, hand_data, self.current_mode,
                    fps, is_failsafe=is_failsafe,
                    click_info=self.click_indicator,
                    scroll_delta=scroll_delta
                )

                # Display frame
                cv2.imshow("KINETIC-OS", display_frame)

                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n[KINETIC-OS] Quit key pressed. Exiting...")
                    break

        except KeyboardInterrupt:
            print("\n[KINETIC-OS] Interrupted. Exiting...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Release resources."""
        print("[KINETIC-OS] Cleaning up...")
        self.hand_engine.close()
        self.cap.release()
        cv2.destroyAllWindows()
        print("[KINETIC-OS] Goodbye!")


def main():
    """Entry point for KINETIC-OS."""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██╗  ██╗██╗███╗   ██╗███████╗████████╗██╗ ██████╗           ║
    ║   ██║ ██╔╝██║████╗  ██║██╔════╝╚══██╔══╝██║██╔════╝           ║
    ║   █████╔╝ ██║██╔██╗ ██║█████╗     ██║   ██║██║                ║
    ║   ██╔═██╗ ██║██║╚██╗██║██╔══╝     ██║   ██║██║                ║
    ║   ██║  ██╗██║██║ ╚████║███████╗   ██║   ██║╚██████╗           ║
    ║   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝ ╚═════╝           ║
    ║                          -OS-                                 ║
    ║                                                               ║
    ║   Contactless Hand-Gesture Interface for Linux               ║
    ║   Production-Grade | Butter-Smooth Precision                  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    try:
        app = KineticOS()
        app.run()
    except RuntimeError as e:
        print(f"[KINETIC-OS] Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[KINETIC-OS] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
