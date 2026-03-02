import cv2
import numpy as np
import math

def calculate_angle(x1, y1, x2, y2):
    """Calculates the angle of the line relative to the x-axis."""
    x_diff = x2 - x1
    y_diff = y2 - y1
    # Note: y-axis is inverted in images (0 is top)
    angle = math.degrees(math.atan2(y_diff, x_diff))
    return angle

def read_gauge_pressure(image_path, min_val=0, max_val=2.5, min_angle=135, max_angle=405):
    """
    Reads a cropped gauge image and returns the estimated pressure.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read image.")

    height, width = img.shape[:2]
    center_x, center_y = width // 2, height // 2

    # 1. Convert to grayscale and increase blur slightly to ignore thin background dial lines
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # MAGIC UPGRADE 1: Otsu's Thresholding
    # Instead of a hardcoded 100, this automatically calculates the optimal threshold for the specific lighting of each photo
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 2. Edge detection
    edges = cv2.Canny(thresh, 50, 150, apertureSize=3)

    # MAGIC UPGRADE 2: More forgiving line detection
    # We lowered the threshold to 30, shortened the min length, and increased the gap allowed between broken line segments
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30, minLineLength=height//5, maxLineGap=20)

    if lines is None:
        return {"error": "No needle detected."}

    best_line = None
    max_length = 0

    # MAGIC UPGRADE 3: Wider center tolerance
    # Since YOLO isn't cropping the dial perfectly yet, we increase tolerance to 35% of the image width
    tolerance = width * 0.35
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        dist1 = math.sqrt((x1 - center_x)**2 + (y1 - center_y)**2)
        dist2 = math.sqrt((x2 - center_x)**2 + (y2 - center_y)**2)

        if dist1 < tolerance or dist2 < tolerance:
            if length > max_length:
                max_length = length
                if dist1 < dist2:
                    best_line = (x1, y1, x2, y2)
                else:
                    best_line = (x2, y2, x1, y1)

    if best_line is None:
        return {"error": "Needle found, but it didn't align with the center of the image."}

    x_center, y_center, x_tip, y_tip = best_line
    
    # Calculate standard angle (0 is Right, 90 is Up, 180 is Left)
    angle = math.degrees(math.atan2(y_center - y_tip, x_tip - x_center)) % 360

    # Standard gauges move CLOCKWISE, meaning the angle DECREASES as pressure INCREASES.
    # For this gauge: min value is at ~225° (bottom left), max is at ~315° (bottom right)
    start_angle = 225
    total_sweep = 270 
    
    # Calculate how far along the sweep the needle is (Percentage from 0.0 to 1.0)
    progress = (start_angle - angle) % 360 / total_sweep
    
    val_range = max_val - min_val
    pressure = min_val + (progress * val_range)
    
    # Cap the pressure to prevent wild readings if it reads the tail of the needle
    pressure = max(min_val, min(max_val, pressure))

    return {
        "pressure": round(pressure, 2),
        "angle": round(angle, 2)
    }
# Quick test if you run this file directly
if __name__ == "__main__":
    # You can put a cropped gauge image in backend/test_images/ to test this
    # print(read_gauge_pressure("test_images/crop.jpg"))
    pass