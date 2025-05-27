from gradio_client import Client, file
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tempfile
import os
import cv2, os, sys
import numpy as np
from PIL import Image

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from cycle_detect import *
from config import ANIME_ADDRESS, CONTOUR_ADDRESS, OPEN_ADDRESS, PS_ADDRESS, ADD_DOT


sk_type = os.getenv("sk_type", "open")
if sk_type == "ps":
    sk_client = Client(PS_ADDRESS)
elif sk_type == "anime":
    sk_client = Client(ANIME_ADDRESS)
elif sk_type == "contour":
    sk_client = Client(CONTOUR_ADDRESS)
elif sk_type == "open":
    sk_client = Client(OPEN_ADDRESS)

def canny(image: Image.Image, low_threshold: int = 50, high_threshold: int = 200) -> Image.Image:
    """
    Perform Canny edge detection and return a black-and-white edge map.

    Args:
        image (PIL.Image.Image): The input image.
        low_threshold (int): Lower threshold for edge detection.
        high_threshold (int): Upper threshold for edge detection.

    Returns:
        PIL.Image.Image: Black-and-white edge map.
    """
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    blur  = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blur, low_threshold, high_threshold)
    inverted = cv2.bitwise_not(edges)
    return Image.fromarray(inverted)

def binary(image: Image.Image, threshold: int = 127, max_value: int = 255, method: int = cv2.THRESH_BINARY) -> Image.Image:
    """
    Convert an image to binary (black and white) using thresholding.

    Args:
        image (PIL.Image.Image): The input image.
        threshold (int): Threshold value for binarization (0-255).
        max_value (int): Maximum value to use for the binary image.
        method (int): OpenCV thresholding method, default is cv2.THRESH_BINARY.
                     Other options include:
                     - cv2.THRESH_BINARY_INV (inverted binary)
                     - cv2.THRESH_TRUNC
                     - cv2.THRESH_TOZERO
                     - cv2.THRESH_TOZERO_INV

    Returns:
        PIL.Image.Image: Binary (black and white) image.
    """
    img_array = np.array(image)
    
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    _, binary_img = cv2.threshold(blur, threshold, max_value, method)
    
    return Image.fromarray(binary_img)

def sketch(image: Image.Image):
    """
    Generate a sketch-style object image using sketching tool, tailored for reference image in blink sem_corr task.
    
    Args:
        image (PIL.Image.Image): The input image.
    
    Returns:
        PIL.Image.Image: The generated sketch image.
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        image.save(tmp_file.name, 'JPEG')
        image = tmp_file.name
        
        outputs = sk_client.predict(file(image))
    
        output_image = Image.open(outputs)
        if ADD_DOT:
            circles = detect_red_circles(Image.open(image))
            output_image = draw_circles_on_image(output_image, circles)
        else:
            circles = []

    return output_image


def dot_matrix_two_dimensional(img, dots_size_w = 6, dots_size_h = 6):
    """
    takes an original image as input, save the processed image to save_path. Each dot is labeled with two-dimensional Cartesian coordinates (x,y). Suitable for single-image tasks.
    control args:
    1. dots_size_w: the number of columns of the dots matrix
    2. dots_size_h: the number of rows of the dots matrix
    """
    if img.mode != 'RGB':
        img = img.convert('RGB')
    draw = ImageDraw.Draw(img, 'RGB')

    width, height = img.size
    grid_size_w = dots_size_w + 1
    grid_size_h = dots_size_h + 1
    cell_width = width / grid_size_w
    cell_height = height / grid_size_h

    font = ImageFont.load_default()
    
    count = 0
    for j in range(1, grid_size_h):
        for i in range(1, grid_size_w):
            x = int(i * cell_width)
            y = int(j * cell_height)

            pixel_color = img.getpixel((x, y))
            # choose a more contrasting color from black and white
            if pixel_color[0] + pixel_color[1] + pixel_color[2] >= 255 * 3 / 2:
                opposite_color = (0,0,0)
            else:
                opposite_color = (255,255,255)

            circle_radius = width // 240  # Adjust dot size if needed; default == width // 240
            draw.ellipse([(x - circle_radius, y - circle_radius), (x + circle_radius, y + circle_radius)], fill=opposite_color)

            text_x, text_y = x + 3, y
            count_w = count // dots_size_w
            count_h = count % dots_size_w
            label_str = f"({count_w+1},{count_h+1})"
            draw.text((text_x, text_y), label_str, fill=opposite_color, font=font)
            count += 1
    return img