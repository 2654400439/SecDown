import json

def generate_baseline_prompt(task_json):
    nl_goal = task_json["nl_goal"]
    method = task_json["network_requirements"]["method"]
    url = task_json["network_requirements"]["target_url"]
    params = task_json["network_requirements"]["params"]
    headers = task_json["network_requirements"]["headers"]
    payload = task_json["network_requirements"]["payload"]

    prompt = f"""You are an expert Python developer.

Task Goal: {nl_goal}

Please write a complete, runnable Python script to accomplish this. 
You MUST strictly adhere to the following network configuration to ensure the API call succeeds:
- HTTP Method: {method}
- Target URL: {url}
"""
    if params:
        prompt += f"- Query Parameters: {params}\n"
    if headers:
        prompt += f"- Headers: {headers}\n"
    if payload:
        prompt += f"- JSON Payload: {payload}\n"

    return prompt





if __name__ == "__main__":
    task_file = '../type_a/2_github_bug_reports.json'

    task_json = json.loads(open(task_file).read())
    print(generate_baseline_prompt(task_json))