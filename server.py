from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import argparse
import json
import asyncio
import os

app = FastAPI()

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = f'https://api.runpod.ai/v2/{ENDPOINT_ID}'

def transform_request(openai_request):
    transformed_request = {
            k: v for k, v in openai_request.items()
    }
    print(transformed_request)
    return transformed_request

async def stream_data(run_url, headers, test_payload):
    response = requests.post(run_url, headers=headers, data=json.dumps({"input": test_payload}))
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error initializing the stream")

    job_id = response.json().get("id")
    stream_url = BASE_URL + f'/stream/{job_id}'
    response = {}

    while response.get('status') != 'COMPLETED':
        response = requests.get(stream_url, headers=headers).json()
        stream = response.get('stream', [])
        if stream:
            for chunk in stream:
                yield chunk["output"]
        await asyncio.sleep(0.1)  

@app.post("/v1/chat/completions")
async def create_chat_completion(request: Request, background_tasks: BackgroundTasks):
    # Extract the RunPod API key from the request header
    runpod_api_key = request.headers.get('Authorization')
    if not runpod_api_key:
        raise HTTPException(status_code=400, detail="RunPod API key is missing in the request headers")

    openai_request = await request.json()
    transformed_request = transform_request(openai_request)

    headers = {'Authorization': runpod_api_key, 'Content-Type': 'application/json'}
    run_url = BASE_URL + "/run"

    return StreamingResponse(stream_data(run_url, headers, transformed_request))

@app.get("/v1/models")
async def get_model():
    """
    Endpoint to return the model name.
    """
    return JSONResponse(content={"model": MODEL_NAME})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
