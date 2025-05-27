import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def is_center_red(hsv_img, x, y):
    patch = hsv_img[y-1:y+2, x-1:x+2]
    hs = patch[..., 0].flatten()
    red_pixels = ((hs <= 10) | (hs >= 170)).sum()
    ratio = red_pixels / hs.size
    return ratio > 0.5

def detect_red_circles(image: Image.Image):
    image = np.array(image).astype(np.uint8)

    lower_red = np.array([210, 0, 0])
    upper_red = np.array([255, 35, 35])

    red_mask = cv2.inRange(image, lower_red, upper_red)
    red_only = cv2.bitwise_and(image, image, mask=red_mask)
    gray = cv2.cvtColor(red_only, cv2.COLOR_RGB2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    
    circles = cv2.HoughCircles(
        gray_blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=20,
        param1=50,
        param2=15,       
        minRadius=5,
        maxRadius=25
    )
    detected_circles = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for x, y, r in circles[0]:
            detected_circles.append([[x, y], r])

    return detected_circles


def draw_circles_on_image(image: Image.Image, circles):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=45)
    for circle in circles:
        x, y = circle[0]
        r = circle[1] * 1.8
        draw.ellipse((x - r, y - r, x + r, y + r), outline="red", width=17)

        text_position = (x - 100, y - r - 20)
        # draw.text(text_position, "REF", fill="green", font=font, stroke_width=3, stroke_fill="black")
        
    return image

