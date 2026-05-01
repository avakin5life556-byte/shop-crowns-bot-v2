class SessionManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, user_id: int, data: dict = None):
        self.sessions[user_id] = data or {}

    def get_session(self, user_id: int):
        return self.sessions.get(user_id, {})

    def update_session(self, user_id: int, data: dict):
        if user_id not in self.sessions:
            self.sessions[user_id] = {}
        self.sessions[user_id].update(data)

    def delete_session(self, user_id: int):
        if user_id in self.sessions:
            del self.sessions[user_id]


# instance جاهز للاستخدام
session_manager = SessionManager()
