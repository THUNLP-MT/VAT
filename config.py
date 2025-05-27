import os

MAX_REPLY = 10
ADD_DOT = os.getenv("ADD_DOT", "0") == "1"
MODEL = os.getenv("MODEL", "gpt-4o-2024-11-20")

os.environ['OPENAI_BASE_URL'] = os.environ.get('OPENAI_BASE_URL')
os.environ["AUTOGEN_USE_DOCKER"] = "False"

if "gpt-4o" in MODEL:
    llm_config={"cache_seed": None, "config_list": [{"model": "gpt-4o-2024-11-20", "temperature": 0.0, "api_key": os.environ.get("OPENAI_API_KEY")}]}
    
if "gemini" in MODEL:
    llm_config={"cache_seed": None, "config_list": [{"model": "gemini-2.0-pro-exp-02-05", "temperature": 0.0, "api_key": os.environ.get("OPENAI_API_KEY")}]}
    
if "qwen32" in MODEL:
    llm_config={"cache_seed": None, "config_list": [{"model": "qwen2.5-vl-32b-instruct", "temperature": 0.0, "api_key": os.environ.get("OPENAI_API_KEY")}]}
    
if "cpm" in MODEL:
    llm_config={"cache_seed": None, "config_list": [{"model": "MiniCPM-V-2_6", "temperature": 0.0, "api_key": os.environ.get("OPENAI_API_KEY")}]}
    os.environ['OPENAI_BASE_URL'] = "http://localhost:4000/v1"
    
if "qwen" in MODEL and "7" in MODEL:
    llm_config={"cache_seed": None, "config_list": [{"model": "qwen2.5-7b-vl", "temperature": 0.001, "api_key": os.environ.get("OPENAI_API_KEY")}]}
    os.environ['OPENAI_BASE_URL'] = "http://localhost:4001/v1"
    
if "qwen" in MODEL and "3" in MODEL:
    llm_config={"cache_seed": None, "config_list": [{"model": "qwen2.5-3b-vl", "temperature": 0.0, "api_key": os.environ.get("OPENAI_API_KEY")}]}
    os.environ['OPENAI_BASE_URL'] = "http://localhost:4002/v1"

PS_ADDRESS = "http://localhost:8083/"
ANIME_ADDRESS = "http://localhost:8084/"
CONTOUR_ADDRESS = "http://localhost:8085/"
OPEN_ADDRESS = "http://localhost:8086/"
