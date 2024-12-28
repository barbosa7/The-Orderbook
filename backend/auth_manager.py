from dataclasses import dataclass
from typing import Dict, Optional
import hashlib
import os
import jwt
import requests
import time
from backend.logger import logger
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key')  # In production, always use env var

@dataclass
class User:
    username: str
    password_hash: str
    is_admin: bool = False

class AuthManager:
    def __init__(self):
        self.users: Dict[str, User] = {}
    
    def create_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        if username in self.users:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.users[username] = User(username, password_hash, is_admin)
        logger.info(f"Created user: {username}")
        return True 

    def verify_user(self, username: str, password: str) -> Optional[str]:
        logger.info(f"Verifying user: {username}")
        user = self.users.get(username)
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user.password_hash:
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        token_data = {
            "username": username,
            "is_admin": user.is_admin,
            "exp": int(time.time()) + 86400  # 24 hour expiration
        }
        return jwt.encode(token_data, SECRET_KEY, algorithm="HS256")

    def verify_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = payload["username"]
            user = self.users.get(username)
            if user:
                return User(username=username, password_hash=user.password_hash, is_admin=user.is_admin)
            return None
        except jwt.InvalidTokenError:
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user_data = self.users.get(username)
        if not user_data:
            return None
            
        if user_data["password"] != password:
            return None
            
        return user_data["user"]
        
    def create_token(self, user: User) -> str:
        return f"token_{user.username}"  # Simple token for demo