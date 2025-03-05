from datetime import datetime
import os
import tempfile
import uuid
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from zaia_agents.crew import ZaiaAgents
from mem0 import MemoryClient

class MessageInput(BaseModel):
    role: str
    content: str
class ChatInput(BaseModel):
    query: str
    user_id: str
    messages: list[MessageInput]
    file_in: UploadFile = None
class ChatOutput(BaseModel):
    result: str
    user_id: str
    messages: list[MessageInput]

router = APIRouter()
response_status = {}

@router.get("/")
def read_root():
    return {"message": "Hello World"}

@router.get("/status/{user_id}")
def get_status(user_id: str):
    status = response_status.get(user_id, "not started")
    return {"status": status}

# @router.get("/chat/{user_id}")
# async def get_chat(user_id: str):
#     response_status[user_id] = "processing"
#     try:
#         result = ZaiaAgents(user_id=user_id).crew().kickoff(inputs={"current_time": str(datetime.now())})
#         response_status[user_id] = "completed"
#         return {"result": str(result), "user_id": user_id}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred while running the crew: {e}")

@router.post("/chat/{user_id}", response_model=ChatOutput)
async def chat_endpoint(user_id: str, query: str = Form(...), file_in: UploadFile = File(None), messages: str = Form(...)):
    response_status[user_id] = "processing"
    inputs = {
        'query': query,
        'file_path': None,
        'current_time': str(datetime.now())
    }
    file_path = None
    if file_in is not None and file_in != "":
        file_bytes = await file_in.read()
        temp_dir = tempfile.gettempdir()
        unique_id = uuid.uuid4().hex
        file_path = os.path.join(temp_dir, f"{unique_id}_{file_in.filename}")
        
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        inputs['file_size'] = len(file_bytes)
        inputs['file_path'] = file_path
    try:
        parsed_messages = json.loads(messages)
        client = MemoryClient(api_key=os.environ['MEM0_API_KEY'])
        client.add(parsed_messages, user_id=user_id)
        if file_path is not None:  
            result = ZaiaAgents(file_path=file_path, user_id=user_id, messages=messages).crew().kickoff(inputs=inputs)
        else:            
            result = ZaiaAgents(user_id=user_id, messages=messages).crew().kickoff(inputs=inputs)
        parsed_messages.append({
            "role": "user",
            "content": query
        })
        parsed_messages.append({
            "role": "assistant",
            "content": str(result)
        })
        response_status[user_id] = "completed"
        return {"result": str(result), "user_id": user_id, "messages": parsed_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while running the crew: {e}")

@router.get("/error")
def error_route():
    raise HTTPException(status_code=500, detail="Intentional Error")

