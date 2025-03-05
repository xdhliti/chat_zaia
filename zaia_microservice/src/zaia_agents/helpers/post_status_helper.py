# src/zaia_agents/utils/status_utils.py

class PostStatusHelper:
    def __init__(self):
        self._status = {}

    def set_status(self, user_id: str, status: str) -> None:
        """Define ou atualiza o status para um usuário específico."""
        self._status[user_id] = status

    def get_status(self, user_id: str) -> str:
        """Retorna o status do usuário ou 'not_found' se não existir."""
        return self._status.get(user_id, "not_found")

    def clear_status(self, user_id: str) -> None:
        """Remove o status do usuário, caso exista."""
        if user_id in self._status:
            del self._status[user_id]
