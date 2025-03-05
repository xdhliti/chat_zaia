from fastapi import APIRouter, HTTPException, Depends
from src.zaia_agents.controllers.status_controller import StatusController
from src.zaia_agents.controllers.chat_controller import ChatController
from src.zaia_agents.models.chat_model import ChatOutput
from src.zaia_agents.models.chat_model import ChatInput
from src.zaia_agents.helpers.post_status_helper import PostStatusHelper

router = APIRouter()
status_controller = StatusController()
status_manager = PostStatusHelper()

@router.post("/{user_id}", response_model=ChatOutput)
def post_chat_message(chat_input: ChatInput = Depends(ChatInput.as_form), user_id: str = None):
    try:
        controller = ChatController(user_id=user_id, chat_input=chat_input, response_status=status_manager)
        controller_response = controller.chat_endpoint()
        return {
            "result": controller_response["result"],
            "user_id": controller_response["user_id"],
            "messages": controller_response["messages"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
def get_status(user_id: str):
    try:
        status = status_manager.get_status(user_id)
        return {"user_id": user_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/error")
def error_route():
    raise HTTPException(status_code=500, detail="Intentional Error")
