from pydantic import BaseModel
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, Form

class MessageInput(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    query: str
    file_in: Optional[UploadFile] = None
    messages: str

    @classmethod
    def as_form(
        cls,
        query: str = Form(...),
        messages: str = Form(...),
        file_in: Optional[UploadFile] = File(None)
    ):
        return cls(query=query, messages=messages, file_in=file_in)

class ChatOutput(BaseModel):
    result: str
    user_id: str
    messages: List[MessageInput]
