from dataclasses import dataclass
import jwt
import time
from typing import Dict, Optional

SECRET_KEY = "your-secret-key"  # In production, use environment variable

@dataclass
class User:
    username: str
    is_admin: bool

class AuthManager:
    def __init__(self):
        self._users: Dict[str, dict] = {}
        
    def create_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        if username in self._users:
            return False
            
        self._users[username] = {
            "password": password,  # In production, use password hashing
            "is_admin": is_admin
        }
        return True
        
    def verify_user(self, username: str, password: str) -> Optional[str]:
        user = self._users.get(username)
        if user and user["password"] == password:
            token = jwt.encode(
                {
                    "sub": username,
                    "is_admin": user["is_admin"],
                    "exp": time.time() + 3600  # 1 hour expiration
                },
                SECRET_KEY,
                algorithm="HS256"
            )
            return token
        return None
        
    def verify_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload["exp"] > time.time():
                return User(
                    username=payload["sub"],
                    is_admin=payload["is_admin"]
                )
        except jwt.InvalidTokenError:
            pass
        return None 