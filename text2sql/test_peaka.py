import json
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv("PEAKA_API_KEY")
GET_URL= "https://partner.peaka.studio/api/v1/info"
POST_URL = "https://partner.peaka.studio/api/v1/ai-agent/{project_id}/chat"
INPUT_FILE= "output.json"
OUTPUT_FILE= "results.json"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}
with open(INPUT_FILE, 'r') as f:
    data=json.load(f)

response= requests.get(GET_URL, headers=headers)
project_info= response.json()

project_id = project_info.get("projectId")  


results=[]
target_databases = {"DELIVERY_CENTER","AIRLINES","DEATH"}
for item in data:
    database = item.get("database")
    question = item.get("instruction")

    if database not in target_databases:
        continue

    body = {
        "message": question}
        
    start_time = time.time()

    response =requests.post(
        POST_URL.format(project_id=project_id),
        headers=headers,
        json=body)
    
    end_time = time.time()
    elapsed_time = round(end_time - start_time)

    if response.status_code == 200:
        reply = response.json()
        content_raw = reply["result"]["messages"][1]["kwargs"]["content"]
        results.append({
            "database": item.get("database"),
            "question": question,
            "result": content_raw,
            "response_time": elapsed_time})
    else:
        results.append({
            "database": item.get("database"),
            "question": question,
            "response_time": elapsed_time,
            "result": f"ERROR {response.status_code}: {response.text}"
            })
    

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False) 