from main import run_agent
import os, glob, argparse
from tqdm import tqdm
import os
from typing import Dict, Any
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import logging
from config import llm_config

from datetime import datetime

def config_to_env_vars():

    if llm_config.get("cache_seed") is not None:
        os.environ['LLM_CONFIG_CACHE_SEED'] = str(llm_config["cache_seed"])
    else:
        os.environ['LLM_CONFIG_CACHE_SEED'] = "None"

    if llm_config.get("config_list") and len(llm_config["config_list"]) > 0:
        config_item = llm_config["config_list"][0]

        if "model" in config_item:
            os.environ['LLM_CONFIG_MODEL'] = config_item["model"]
            print("SET MODEL TO", config_item["model"])
        if "temperature" in config_item:
            os.environ['LLM_CONFIG_TEMPERATURE'] = str(config_item["temperature"])
        os.environ['LLM_CONFIG_API_KEY_SOURCE'] = 'OPENAI_API_KEY'

config_to_env_vars()

TIME = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

ABS_TYPE = os.getenv("ABS_TYPE", "open")
model_info = llm_config["config_list"][0]["model"]

def set_log():

    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f"{args.task}_{model_info}_{ABS_TYPE}_{TIME}.log")

    logging.basicConfig(
        filename=log_filename,
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    class LoggerWriter:
        def __init__(self, level_func):
            self.level_func = level_func

        def write(self, message):
            message = message.strip()
            if message:
                self.level_func(message)

        def flush(self):
            pass

    sys.stdout = LoggerWriter(logging.info)
    sys.stderr = LoggerWriter(logging.error)


def run_task(task, output_dir, task_name=None):
    all_task_instances = glob.glob(f"../../tasks/{task}/processed/*/")
    output_dir = os.path.join(output_dir, f"{task_name}_{model_info}_{ABS_TYPE}_{TIME}")
    for task_instance in tqdm(all_task_instances[:]):
        print(f"Running task instance: {task_instance}")
        run_agent(task_instance, output_dir, task_name=task_name)
        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--task", type=str, help="The task name")
    args = parser.parse_args()
    
    set_log()
    
    task_name = args.task
    run_task(args.task, "outputs", task_name=task_name)
