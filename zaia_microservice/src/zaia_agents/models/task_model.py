# src/zaia_agents/models/task_output_model.py

from pydantic import BaseModel
from typing import Optional

class TaskOutputModel(BaseModel):
    context: Optional[str] = None
    content: Optional[str] = None
