class StatusController:
    def get_status(self, user_id: str, response_status: dict):
        return response_status.get(user_id, "not started")
