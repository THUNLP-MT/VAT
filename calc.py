import os
import json
import re
import argparse
import datetime
import math

args = None

def extract_answer_from_request(request_path):
    try:
        with open(request_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        answer = data.get('answer', '')
        if isinstance(answer, str):
            return answer.strip('() ').upper()
        return str(answer).strip('() ').upper()
    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"Warning: Failed to read or parse request.json {request_path}: {e}")
        return None

def extract_answer_from_output(output_path):
    lst = ["ANSWER", "ANSWER:", "REF", "CELERIAC"]
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data and isinstance(data, list) and len(data) > 0 and \
           data[-1].get('content') and isinstance(data[-1]['content'], list) and \
           len(data[-1]['content']) > 0 and data[-1]['content'][0].get('text'):
            text = data[-1]['content'][0]['text']
            # print(text)
            
            if args.model == "gemini":
                match2 = re.search(r'\\boxed\{([A-Z])\}', text)
                if match2:
                    ans = match2.group(1).strip().upper()
                    if not any(i in ans for i in lst): 
                        return ans
            
            match = re.search(r'answer:.*?\(\s*([A-D])\s*\).*? terminate', text, re.IGNORECASE)
            if match:
                return match.group(1).strip().upper()
            
            match = re.search(r'ANSWER:.*?Point\s+([A-D]).*?TERMINATE', text)
            if match:
                return match.group(1).upper()
            
            match = re.search(r'ANSWER:.*?Point\s+([A-D]).*?TERMINATE', text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
            
            match = re.search(r'answer:\s*\(\s*([a-zA-Z]+)\s*\)', text, re.IGNORECASE)
            if match:
                return match.group(1).strip().upper()
            
            match = re.search(r'answer:.*?\(\s*([a-zA-Z]+)\s*\).*?terminate', text, re.IGNORECASE | re.DOTALL)
            if match:
                ans = match.group(1).strip().upper()
                if not any(i in ans for i in lst): 
                    return ans
                
            match1 = re.search(r'answer:.*?\(?\s*([a-zA-Z]+)\s*\)?', text, re.IGNORECASE | re.DOTALL)
            if match1:
                ans = match1.group(1).strip().upper()
                if not any(i in ans for i in lst): 
                    return ans

            match2 = re.search(r'\(\s*([a-zA-Z]+)\s*\)', text, re.IGNORECASE)
            if match2:
                ans = match2.group(1).strip().upper()
                if not any(i in ans for i in lst): 
                    return ans

            match3 = re.search(r'Point\s+([A-D])', text, re.IGNORECASE)
            if match3:
                return match3.group(1).upper()
        
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None


def extract_answer_from_request_ooo(request_path):
    try:
        with open(request_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        answer = data.get('answer', '')
        if isinstance(answer, str):
            return answer.replace(' ', '').lower()
        return str(answer).replace(' ', '').lower()
    except json.JSONDecodeError:
        return None
    except Exception:
        return None

def extract_answer_from_output_ooo(output_path):
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data and isinstance(data, list) and len(data) > 0 and \
           data[-1].get('content') and isinstance(data[-1]['content'], list) and \
           len(data[-1]['content']) > 0 and data[-1]['content'][0].get('text'):
            text = data[-1]['content'][0]['text']
            
            match = re.search(r'answer:.*?(\(\s*\d+\s*,\s*\d+\s*\))', text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).replace(' ', '').lower()
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None

def parse_log_for_runtime(log_path):
    if not os.path.exists(log_path):
        return None

    start_time = None
    end_time = None
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

            if lines:
                for line in lines:
                    time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', line)
                    if time_match and not start_time:
                        start_time = datetime.datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                        continue
                
                for line in reversed(lines):
                    time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', line)
                    if time_match:
                        end_time = datetime.datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                        break
            
            if start_time and end_time:
                
                time_diff = (end_time - start_time).total_seconds() / 60
                return time_diff
    except Exception as e:
        print(f"Error parsing log file: {log_path}, error: {e}")
    
    return None

def get_log_path_from_output_dir(output_dir, task_run_name):
    
    base_dir = os.path.dirname(os.path.dirname(output_dir))
    log_dir = os.path.join(base_dir, "log")

    if not os.path.exists(log_dir):
        log_dir = os.path.join(base_dir, "logs")
    
    if not os.path.exists(log_dir):
        log_dir = os.path.join(os.path.dirname(output_dir), "log")
        
    if not os.path.exists(log_dir):
        log_dir = os.path.join(os.path.dirname(output_dir), "logs")

    log_path = os.path.join(log_dir, f"{task_run_name}.log")
    if os.path.exists(log_path):
        return log_path
    for ext in ['.txt', '.log.txt', '']:
        log_path = os.path.join(log_dir, f"{task_run_name}{ext}")
        if os.path.exists(log_path):
            return log_path
    
    return None

def calculate_single_task_run_accuracy(task_run_dir, task_type):
    total_tasks = 0
    correct_count = 0
    total_valid_pairs = 0
    
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_all_tokens = 0
    token_count = 0 

    total_cost = 0
    
    accp = {}
    
    for item_name in sorted(os.listdir(task_run_dir)):
        item_path = os.path.join(task_run_dir, item_name)
        if os.path.isdir(item_path): 
            request_path = os.path.join(item_path, 'request.json')
            output_path = os.path.join(item_path, 'output.json')
            token_path = os.path.join(item_path, 'usage_summary.json')

            if os.path.exists(token_path):
                try:
                    with open(token_path, 'r', encoding='utf-8') as f:
                        token_data = json.load(f)
                    
                    # Token count for this task
                    prompt_tokens = 0
                    completion_tokens = 0
                    
                    if "sketch" in task_run_dir.lower():
                        if 'total' in token_data and isinstance(token_data['total'], dict):
                            model_found = False
                            for key, value in token_data['total'].items():
                                if key != 'total_cost' and isinstance(value, dict):
                                    if 'prompt_tokens' in value and 'total_tokens' in value:
                                        prompt_tokens = value.get('prompt_tokens', 0)
                                        completion_tokens = value.get('completion_tokens', 0)
                                        
                                        total_prompt_tokens += prompt_tokens
                                        total_completion_tokens += completion_tokens
                                        total_all_tokens += value.get('total_tokens', 0)
                                        token_count += 1
                                        model_found = True
                                        break
                            
                            if not model_found and 'prompt_tokens' in token_data['total']:
                                prompt_tokens = token_data['total'].get('prompt_tokens', 0)
                                completion_tokens = token_data['total'].get('completion_tokens', 0)
                                
                                total_prompt_tokens += prompt_tokens
                                total_completion_tokens += completion_tokens
                                total_all_tokens += token_data['total'].get('total_tokens', 0)
                                token_count += 1
                    else:
                        for usage_type in ['total', 'actual']:
                            if usage_type in token_data and isinstance(token_data[usage_type], dict):
                                if 'prompt_tokens' in token_data[usage_type]:
                                    prompt_tokens = token_data[usage_type]['prompt_tokens']
                                    completion_tokens = token_data[usage_type].get('completion_tokens', 0)
                                    
                                    total_prompt_tokens += prompt_tokens
                                    total_completion_tokens += completion_tokens
                                    total_all_tokens += token_data[usage_type].get('total_tokens', 0) 
                                    token_count += 1
                                    break
                    # Based on gpt-4o api cost.
                    cost = (prompt_tokens / 1000000) * 5 + (completion_tokens / 1000000) * 20
                    total_cost += cost
                    
                except Exception as e:
                    print(f"Failed to read token data: {token_path}, error: {e}")

            if os.path.exists(request_path) and os.path.exists(output_path):
                total_tasks += 1
                gt, pred = None, None
                if task_type == "ooo":
                    gt = extract_answer_from_request_ooo(request_path)
                    pred = extract_answer_from_output_ooo(output_path)
                elif task_type == "default": 
                    gt = extract_answer_from_request(request_path)
                    pred = extract_answer_from_output(output_path)
                    if pred == "A" and args.model == "gemini" and "mme" in request_path:
                        pred = "YES"
                    if pred == "B" and args.model == "gemini" and "mme" in request_path:
                        pred = "NO"
                else:
                    continue

                if gt is not None and pred is not None:
                    if args.accp == 1 and "mme" in task_run_dir:
                        now = accp.get(item_name.split("_")[0], 0)
                        if gt == pred:
                            accp[item_name.split("_")[0]] = now + 1
                        else:
                            accp[item_name.split("_")[0]] = now
                    
                    total_valid_pairs += 1
                    if gt == pred:
                        correct_count += 1

    avg_tokens = 0
    if token_count > 0:
        avg_tokens = total_all_tokens / token_count

    avg_cost = 0
    if total_tasks > 0:
        avg_cost = total_cost / total_tasks
    
    if args.accp == 1 and "mme" in task_run_dir:
        print(accp)
        return sum(1 if v == 2 else 0 for k, v in accp.items()), len(accp), total_tasks, avg_tokens, total_all_tokens, total_cost, avg_cost
    
    return correct_count, total_valid_pairs, total_tasks, avg_tokens, total_all_tokens, total_cost, avg_cost


def main():
    global args
    parser = argparse.ArgumentParser(description="Calculate accuracy for task runs.")
    parser.add_argument("output_dir", type=str, help="output directory containing task runs")
    parser.add_argument("--abs-type", type=str, default="", help="visual abstract type")
    parser.add_argument("--accp", type=int, default=0, help="whether implement acc+(for MMEs)")
    parser.add_argument("--model", type=str, default="", help="model name")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"Warning: Directory not found: {args.output_dir}")
        return

    overall_results = {}
    print(f"Processing all task runs in directory: {args.output_dir}\n")

    for task_run_name in sorted(os.listdir(args.output_dir)):
        task_run_path = os.path.join(args.output_dir, task_run_name)
        
        if os.path.isdir(task_run_path):
            if not args.abs_type in task_run_name:
                continue
            log_path = get_log_path_from_output_dir(args.output_dir, task_run_name)
            runtime_minutes = None
            if log_path:
                runtime_minutes = parse_log_for_runtime(log_path)
            
            task_type = "default" 
            if "ooo" in task_run_name.lower() or "fig1-case" in task_run_name.lower():
                task_type = "ooo"

            correct, total_valid, total_tasks, avg_tokens, total_tokens, total_cost, avg_cost = calculate_single_task_run_accuracy(task_run_path, task_type)

            if total_valid > 0:
                accuracy = (correct / total_valid) * 100
                overall_results[task_run_name] = {
                    "accuracy": accuracy, 
                    "correct": correct, 
                    "total": total_valid, 
                    "type": task_type, 
                    "tasks": total_tasks,
                    "avg_tokens": avg_tokens,
                    "total_tokens": total_tokens,
                    "total_cost": total_cost,
                    "avg_cost": avg_cost,
                    "runtime_minutes": runtime_minutes
                }
            else:
                overall_results[task_run_name] = {
                    "accuracy": 0, 
                    "correct": 0, 
                    "total": 0, 
                    "type": task_type, 
                    "tasks": total_tasks,
                    "avg_tokens": avg_tokens,
                    "total_tokens": total_tokens,
                    "total_cost": total_cost,
                    "avg_cost": avg_cost,
                    "runtime_minutes": runtime_minutes
                }

    print("\n========== Summary ==========")
    if not overall_results:
        print("No task runs found or processed.")
        return

    # Determine column width for pretty print
    max_name_len = max(len(name) for name in overall_results.keys()) if overall_results else 20
    max_type_len = max(len(data['type']) for data in overall_results.values()) if overall_results else 10
    
    header = f"{'Task Run':<{max_name_len-4}} | {'Type':<{max_type_len-3}} | {'Accuracy':<7} | {'Stats':<6} | {'Tasks':<5} | {'AvgToken':<8} | {'TotalCost($)':<7} | {'AvgCost':<7} | {'Runtime(min)':<10}"
    print(header)
    print("=" * (len(header)+20))

    total_overall_cost = 0
    total_overall_tokens = 0
    total_task_count = 0
    
    for task_run_name, data in overall_results.items():
        stats = f"({data['correct']}/{data['total']})"
        runtime_str = f"{data['runtime_minutes']:.2f}" if data['runtime_minutes'] is not None else "N/A"
        total_cost_str = f"{data['total_cost']:.4f}"
        avg_cost_str = f"{data['avg_cost']:.4f}"
        
        total_overall_cost += data['total_cost']
        total_overall_tokens += data['total_tokens']
        total_task_count += data['tasks']
        
        print(f"{task_run_name:<{max_name_len}} | {data['type']:<{max_type_len}} | {data['accuracy']:<7.2f}% | {stats:<9} | {data['tasks']:<8} | {data['avg_tokens']:<10.1f} | {total_cost_str:<8} | {avg_cost_str:<8} | {runtime_str:<10}")
        print('-' * (len(header)+10))
    
    overall_avg_cost = 0
    if total_task_count > 0:
        overall_avg_cost = total_overall_cost / total_task_count
    
    print(f"{'Total':<{max_name_len}} | {'':^{max_type_len}} | {'':^7} | {'':^9} | {total_task_count:<8} | {'':^10} | ${total_overall_cost:<7.4f} | ${overall_avg_cost:<7.4f} | {'':^10}")
    print("=" * (len(header)+20))
    
    
if __name__ == "__main__":
    main()