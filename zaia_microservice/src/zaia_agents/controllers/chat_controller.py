import json
import os
from datetime import datetime
from fastapi import UploadFile
from src.zaia_agents.services.crew_service import ZaiaAgents as ZaiaChatService
from src.zaia_agents.helpers.memory_helper import MemoryClientHelper
from src.zaia_agents.helpers.file_helper import save_uploaded_file
from src.zaia_agents.models.chat_model import ChatInput

class ChatController:
    def __init__(self, user_id: str, chat_input: ChatInput, response_status: dict):
        self.user_id = user_id
        self.query = chat_input.query
        self.file_in = chat_input.file_in
        self.messages = chat_input.messages
        self.response_status = response_status

    def chat_endpoint(self):

        self.response_status.set_status(self.user_id, "processing")
        
        inputs = {
            "query": self.query,
            "file_path": None,
            "current_time": str(datetime.now()),
        }

        file_path = None
        if self.file_in is not None:
            file_path = save_uploaded_file(self.file_in)
            if file_path is not None and file_path != "":
                inputs["file_path"] = file_path

        try:

            client = MemoryClientHelper()
            client.add(json.loads(self.messages), self.user_id)

            if file_path:
                result = ZaiaChatService(
                    file_path=file_path, 
                    user_id=self.user_id, 
                    messages=self.messages
                ).crew().kickoff(inputs=inputs)
            else:
                result = ZaiaChatService(
                    user_id=self.user_id, 
                    messages=self.messages
                ).crew().kickoff(inputs=inputs)
            parsed_messages = json.loads(self.messages)
            parsed_messages.append({"role": "user", "content": self.query})
            parsed_messages.append({"role": "assistant", "content": str(result)})

            self.response_status.set_status(self.user_id, "completed")

            return {
                "result": str(result),
                "user_id": self.user_id,
                "messages": parsed_messages,
            }
        except Exception as e:
            self.response_status.set_status(self.user_id, "error")
            raise e
