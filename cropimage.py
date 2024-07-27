import cv2
import numpy as np
from flask import jsonify

def detect_and_crop_face(image_bytes, heightPx, widthPx):
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Load pre-trained face detector model
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        if len(faces) == 0:
            return None, img  # No face detected, return original image

        # Sort faces by area (largest face first)
        faces = sorted(faces, key=lambda x: -x[2] * x[3])

        # Take the largest face (assuming it's the closest or main face)
        x, y, w, h = faces[0]

        # Calculate crop coordinates (chest to head)
        y_top = max(0, y - int(h * 0.5))  # Adjust top margin
        y_bottom = min(img.shape[0], y + h + int(h * 0.4))  # Adjust bottom margin

        # Adjust width to maintain aspect ratio centered on face
        target_width = y_bottom - y_top  # Adjust width based on height difference

        # Calculate x coordinates based on the center of the face
        center_x = x + w // 2
        x_left = max(0, center_x - target_width // 2)
        x_right = min(img.shape[1], center_x + target_width // 2)

        # Crop the face region
        cropped_face = img[y_top:y_bottom, x_left:x_right]

        # Create a transparent background canvas of the same size as cropped_face
        background = np.zeros((heightPx, widthPx, 4), dtype=np.uint8)

        # Resize the cropped face to fit the target dimensions
        resized_face = cv2.resize(cropped_face, (widthPx, heightPx))

        # Add alpha channel to resized face
        resized_face_with_alpha = cv2.cvtColor(resized_face, cv2.COLOR_BGR2BGRA)

        # Ensure the cropped face is pasted onto the transparent background correctly
        paste_y = (background.shape[0] - resized_face_with_alpha.shape[0]) // 2
        paste_x = (background.shape[1] - resized_face_with_alpha.shape[1]) // 2

        # Paste resized face onto the transparent background
        background[paste_y:paste_y + resized_face_with_alpha.shape[0], paste_x:paste_x + resized_face_with_alpha.shape[1]] = resized_face_with_alpha

        # Encode the cropped image to bytes
        _, cropped_image_bytes = cv2.imencode('.png', background)
        return cropped_image_bytes.tobytes(), img

    except Exception as e:
        print(f"Error detecting and cropping face: {e}")
        raise
