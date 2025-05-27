import json
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image as PILImage
import base64
from io import BytesIO

def image_to_base64(pil_img):
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    img_byte = buffered.getvalue()
    img_base64 = base64.b64encode(img_byte)
    return img_base64.decode('utf-8')


def custom_encoder(obj):
    if isinstance(obj, Image.Image):
        return image_to_base64(obj)
    return json.JSONEncoder().default(obj)
