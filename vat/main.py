import os
import json
import shutil
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import llm_config
from utils import custom_encoder
from openai import OpenAI
import base64, mimetypes
import re
from PIL import Image
from typing import Dict, Any

sk_type = os.getenv("sk_type", "open")
if sk_type == "binary":
    from tools import binary as sketch
elif sk_type == "canny":
    from tools import canny as sketch
else:
    from tools import sketch
    
def env_vars_to_config() -> Dict[str, Any]:
    cache_seed_str = os.environ.get('LLM_CONFIG_CACHE_SEED', 'None')
    cache_seed = None if cache_seed_str == 'None' else json.loads(cache_seed_str)
    
    model = os.environ.get('LLM_CONFIG_MODEL', '')
    
    temp_str = os.environ.get('LLM_CONFIG_TEMPERATURE', '0.0')
    temperature = float(temp_str)

    api_key_source = os.environ.get('LLM_CONFIG_API_KEY_SOURCE', 'OPENAI_API_KEY')
    api_key = os.environ.get(api_key_source)

    llm_config = {
        "cache_seed": cache_seed,
        "config_list": [
            {
                "model": model,
                "temperature": temperature,
                "api_key": api_key
            }
        ]
    }
    
    return llm_config

def remove_img_tags(text):
    """Remove <img> tags from the query text."""
    return re.sub(r'<img[^>]*>', '', text)

def to_data_uri(path: str) -> str:
    """Convert an image file to a data URI."""
    mime, _ = mimetypes.guess_type(path)
    mime = mime or "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"

def image_to_data_uri(image, format="JPEG"):
    """Convert a PIL Image to a data URI."""
    import io
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    mime = f"image/{format.lower()}"
    b64 = base64.b64encode(buffer.read()).decode()
    return f"data:{mime};base64,{b64}"

def run_agent(task_input, output_dir, task_name=None):
    """Run a simple LLM baseline agent on one task instance.

    Args:
        task_input (str): a path to the task input directory
        output_dir (str): a path to the directory where the output will be saved
        task_name (str, optional): Only needed for math tasks. Defaults to None.
    """

    llm_config = env_vars_to_config()
    print(llm_config["config_list"][0])
    task_input = task_input.rstrip('/')
    task_directory = os.path.join(output_dir, os.path.basename(task_input))
    
    if os.path.exists(task_directory):
        print(f"Task directory {task_directory} already exists. Skipping.")
        return

    os.makedirs(output_dir, exist_ok=True)
    shutil.copytree(task_input, task_directory, dirs_exist_ok=True)
    
    task_metadata = json.load(open(os.path.join(task_input, "request.json")))
    query = task_metadata['query']
    images = task_metadata['images']
    
    data_urls = []
    sketch_urls = []
    sketch_paths = []

    for i, img_path in enumerate(images):
        data_urls.append(to_data_uri(img_path))
        
        original_image = Image.open(img_path)
        sketch_image = sketch(original_image)
        
        sketch_filename = f"sketch_{i+1}_{os.path.basename(img_path)}"
        sketch_path = os.path.join(task_directory, sketch_filename)
        sketch_image.save(sketch_path)
        sketch_paths.append(sketch_path)
        
        sketch_urls.append(image_to_data_uri(sketch_image))

    prompt = (f"{query}\n\n"
              "Each image will be provided together with a corresponding sketch, which is directly converted from the original image. The sketch helps you determine essential components in the image, including but not limited to spatial, structural, relational, and conceptual features, which can assist in your reasoning process.You should use both the original image and the sketch to inform your reasoning process. Sketches are really useful, you must fully utilize them to achieve the best performance. \n"
              "You should reply in the following format: \nANSWER: (your answer). For example: ANSWER: (A). Your answer:\n")
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful Multimodal assistant.\n"
            )
        },
        {
            "role": "user",
            "content": []
        }
    ]
    for i, orig_url in enumerate(data_urls):
        messages[1]['content'].append({"type": "text", "text": f"[image {i+1}]:"})
        messages[1]['content'].append(
            {
                "type": "image_url",
                "image_url": {"url": orig_url}
            }
        )
    for i, sketch_url in enumerate(sketch_urls):
        messages[1]['content'].append({"type": "text", "text": f"[sketch of image {i+1}]:"})
        messages[1]['content'].append(
            {
                "type": "image_url",
                "image_url": {"url": sketch_url}
            }
        )
    messages[1]['content'].append({"type": "text", "text": prompt})
    model_info = llm_config["config_list"][0]
    client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=model_info["api_key"]
    )

    response = None
    try:
        i = 0
        while True:
            i += 1
            response = client.chat.completions.create(
                model=model_info["model"],
                messages=messages,
                temperature=model_info.get("temperature", 0),
                max_tokens=model_info.get("max_tokens", 2048)
            )
            reply = response.choices[0].message.content.strip()
            if reply != "" or i >= 5:
                break
    except Exception as e:
        reply = f"[ERROR] {str(e)}"
    
    messages.append(
        {
            "role": "assistant",
            "content": (
                [{"type": "text", "text": reply}]
            )
        }
    )
    all_messages = [
        {"role": "user", "content": [{"type": "text", "text": prompt}]},
        {"role": "assistant", "content": [{"type": "text", "text": reply}]}
    ]
    all_messages = messages
    
    with open(os.path.join(task_directory, "output.json"), "w") as f:
        json.dump(all_messages, f, indent=4, default=custom_encoder)
    
    usage_summary = {
        'total': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
        'actual': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
        'model': model_info["model"]
    }

    if hasattr(response, 'usage') and response.usage:
        for usage_type in ['total', 'actual']:
            usage_summary[usage_type]['prompt_tokens'] = response.usage.prompt_tokens
            usage_summary[usage_type]['completion_tokens'] = response.usage.completion_tokens
            usage_summary[usage_type]['total_tokens'] = response.usage.total_tokens
    
    with open(os.path.join(task_directory, "usage_summary.json"), "w") as f:
        json.dump(usage_summary, f, indent=4)