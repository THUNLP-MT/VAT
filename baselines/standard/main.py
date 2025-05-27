import os
import sys
sys.path.append("..")
import json
import shutil
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import llm_config
from utils import custom_encoder
from openai import OpenAI
import base64, mimetypes
import re
from typing import Dict, Any

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


def to_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    mime = mime or "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def remove_img_tags(text):
    return re.sub(r'<img[^>]*>', '', text)

def run_agent(task_input, output_dir, task_type="vision", task_name=None):

    assert task_type in ["vision", "math", "geo"]
    llm_config = env_vars_to_config()
    
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
    images = [os.path.join("..", img) for img in images]

    data_urls = [to_data_uri(img) for img in images]
    
    query = remove_img_tags(query)

    prompt = (
        f"{query}\n"
        "please reply in the following format: \nANSWER: (your answer). example: ANSWER: (A) Your response:"
    )

    messages = [{
        "role": "user",
        "content": (
            [{"type": "image_url", "image_url": {"url": url}} for url in data_urls] +
            [{"type": "text", "text": prompt}]
            
        )
    }]

    model_info = llm_config["config_list"][0]
    client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        api_key=model_info["api_key"]
    )
    response = None
    try:
        i = 0
        while True:
            i += 1
            if i == 1:
                tmp = model_info.get("temperature", 0)
            else:
                tmp = 1
            response = client.chat.completions.create(
                model=model_info["model"],
                messages=messages,
                temperature=tmp,
                max_tokens=model_info.get("max_tokens", 2048)
            )
            reply = response.choices[0].message.content.strip()
            if reply != "" or i >= 5:
                break
    except Exception as e:
        reply = f"[ERROR] {str(e)}"
    
    all_messages = [
        {"role": "user", "content": [{"type": "text", "text": query}]},
        {"role": "assistant", "content": [{"type": "text", "text": reply}]}
    ]

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