from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os

# plot digitizer
import cv2
import numpy as np
import matplotlib.pyplot as plt



def extract(path):
    poppler_path = r"C:\Users\Luca\Downloads\poppler\poppler\Library\bin"
    pages = convert_from_path(f'{path}', dpi=300, poppler_path=poppler_path)
    chart_image = pages[6]  # Use the correct page index for your chart
    os.makedirs('./charts', exist_ok=True)
    chart_image.save('./charts/chart.png', 'PNG')
    full_chart_dir = os.path.join(os.path.dirname(__file__), 'charts')
    os.makedirs(full_chart_dir, exist_ok=True)
    chart_image.save(os.path.join(full_chart_dir, 'chart.png'), 'PNG')
    print('PNG saved')

    
    # Load the image
    img = cv2.imread('./charts/chart.png')

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to get binary image (adjust threshold as needed)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Find contours (potential data points)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extract centroid of each contour
    points = []
    for cnt in contours:
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            points.append((cx, cy))

    # Optionally, plot detected points
    for (cx, cy) in points:
        cv2.circle(img, (cx, cy), 5, (0,0,255), -1)

    