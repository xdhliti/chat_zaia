from mem0 import MemoryClient
from src.zaia_agents.models.memory_model import MemoryAddResponse
import os

class MemoryClientHelper:
    def __init__(self):
        self.api_key = os.environ['MEM0_API_KEY']
        self.client = MemoryClient(self.api_key)

    def add(self, messages, user_id, output_format="v1.1") -> MemoryAddResponse:
        data = self.client.add(messages, user_id=user_id, output_format=output_format)
        return MemoryAddResponse(**data)

    def delete_all(self, user_id):
        return self.client.delete_all(user_id)

