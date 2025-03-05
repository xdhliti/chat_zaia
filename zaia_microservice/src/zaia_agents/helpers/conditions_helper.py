# src/utils/conditions_helper.py

import re
from pydantic import ValidationError
from src.zaia_agents.models.task_model import TaskOutputModel

def clean_json_string(json_str: str) -> str:
    cleaned = re.sub(r'```+', '', json_str).strip()
    return cleaned

def weather_condition(task_output) -> bool:
    try:
        raw_str = clean_json_string(task_output.raw)
        data = TaskOutputModel.model_validate_json(raw_str)
        return data.context == "climate"
    except ValidationError:
        return False

def currency_condition(task_output) -> bool:
    try:
        raw_str = clean_json_string(task_output.raw)
        data = TaskOutputModel.model_validate_json(raw_str)
        return data.context == "currency"
    except ValidationError:
        return False

def pdf_reader_condition(task_output) -> bool:
    try:
        raw_str = clean_json_string(task_output.raw)
        data = TaskOutputModel.model_validate_json(raw_str)
        return data.context == "pdf_analysis"
    except ValidationError:
        return False

def pdf_analyzer_condition(task_output) -> bool:
    try:
        raw_str = clean_json_string(task_output.raw)
        data = TaskOutputModel.model_validate_json(raw_str)
        return (data.context == "pdf_analysis") and (data.content and data.content.strip())
    except ValidationError:
        return False

def casual_chat_condition(task_output) -> bool:
    try:
        raw_str = clean_json_string(task_output.raw)
        data = TaskOutputModel.model_validate_json(raw_str)
        return data.context == "casual_chat"
    except ValidationError:
        return False
