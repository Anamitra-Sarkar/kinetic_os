"""
KINETIC-OS Configuration Module
================================
All adjustable settings for the Hand-Gesture Interface.
Modify these values to tune sensitivity and appearance.
"""

# =============================================================================
# CAMERA SETTINGS
# =============================================================================
CAMERA_INDEX = 0  # Default webcam index (0 for built-in, 1+ for external)
CAMERA_WIDTH = 640  # Camera capture width
CAMERA_HEIGHT = 480  # Camera capture height
CAMERA_FPS = 30  # Target frames per second

# =============================================================================
# HAND DETECTION SETTINGS
# =============================================================================
MIN_DETECTION_CONFIDENCE = 0.7  # Minimum confidence for initial detection
MIN_TRACKING_CONFIDENCE = 0.7  # Minimum confidence for landmark tracking
MAX_NUM_HANDS = 1  # Only track one hand for optimal performance

# =============================================================================
# CURSOR SMOOTHING SETTINGS (CRITICAL)
# =============================================================================
# Higher value = smoother but more laggy cursor
# Lower value = more responsive but jittery cursor
# Recommended range: 4 to 10
SMOOTHING_FACTOR = 6

# =============================================================================
# ACTIVE REGION SETTINGS
# =============================================================================
# The "Active Rectangle" in the center of the camera view
# Values are percentages of the camera frame (0.0 to 1.0)
ACTIVE_REGION_X_START = 0.2  # 20% from left edge
ACTIVE_REGION_X_END = 0.8    # 80% from left edge (60% active width)
ACTIVE_REGION_Y_START = 0.2  # 20% from top edge
ACTIVE_REGION_Y_END = 0.8    # 80% from top edge (60% active height)

# =============================================================================
# GESTURE THRESHOLDS
# =============================================================================
# Distance threshold for click detection (normalized coordinates)
# Lower value = requires fingers closer together to trigger click
CLICK_THRESHOLD = 0.05

# Threshold for detecting curled fingers (for fist/scroll detection)
# Lower value = more strict fist detection
CURL_THRESHOLD = 0.08

# Scroll sensitivity (pixels per unit movement)
SCROLL_SENSITIVITY = 10

# =============================================================================
# FAIL-SAFE REGION SETTINGS
# =============================================================================
# Region in top-left corner for emergency exit
# Values are in pixels from the top-left corner
FAILSAFE_X_END = 100  # Width of fail-safe region
FAILSAFE_Y_END = 100  # Height of fail-safe region

# =============================================================================
# HUD COLOR SETTINGS (BGR FORMAT for OpenCV)
# =============================================================================
# Cyberpunk color scheme
COLOR_NEON_GREEN = (57, 255, 20)      # Skeleton lines
COLOR_NEON_RED = (0, 0, 255)          # Active nodes (Thumb, Index tips)
COLOR_NEON_CYAN = (255, 255, 0)       # HUD text and decorations
COLOR_NEON_PURPLE = (255, 0, 128)     # Secondary accent
COLOR_FAILSAFE_RED = (0, 0, 200)      # Fail-safe region
COLOR_BLACK = (0, 0, 0)               # Background elements
COLOR_WHITE = (255, 255, 255)         # General text

# =============================================================================
# HUD VISUAL SETTINGS
# =============================================================================
HUD_LINE_THICKNESS = 2  # Thickness of skeleton lines
HUD_NODE_RADIUS = 8     # Radius of landmark nodes
# Radius of active nodes (Thumb, Index, Middle tips)
HUD_ACTIVE_NODE_RADIUS = 12
HUD_FONT_SCALE = 0.6    # Font size for HUD text
HUD_STATUS_BAR_HEIGHT = 40  # Height of status bar

# =============================================================================
# CLICK DEBOUNCE SETTINGS
# =============================================================================
# Minimum time between clicks in seconds (prevents accidental double-clicks)
CLICK_DEBOUNCE_TIME = 0.3
SCROLL_DEBOUNCE_TIME = 0.05

# =============================================================================
# MODE LABELS
# =============================================================================
MODE_ACTIVE = "ACTIVE"
MODE_SCROLL = "SCROLL"
MODE_IDLE = "IDLE"
