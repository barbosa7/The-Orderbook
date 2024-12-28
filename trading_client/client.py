import requests
import websockets
import json
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable

@dataclass
class MarketUpdate:
    prices: Dict[str, float]
    leaderboard: List[Dict]

class TradingClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_base_url = base_url.replace("http", "ws")
        self.token: Optional[str] = None
        self.market_callback: Optional[Callable[[MarketUpdate], None]] = None
        self.username: Optional[str] = None
        self.session = requests.Session()
    
    def login(self, username: str, password: str) -> bool:
        self.username = username
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False
    
    def place_order(self, competition_id: str, symbol: str, side: str, 
                   quantity: int, price: float) -> bool:
        if not self.token:
            raise ValueError("Not logged in")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.post(
                f"{self.base_url}/order",
                headers=headers,
                json={
                    "competition_id": competition_id,
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "price": price,
                    "user_id": self.username
                }
            )
            if response.status_code == 422:
                error_detail = response.json().get('detail', 'Unknown validation error')
                raise ValueError(f"Invalid order data: {error_detail}")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to place order: {str(e)}")
    
    def join_competition(self, competition_id: str) -> bool:
        if not self.token:
            raise ValueError("Not logged in")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/competition/join",
            headers=headers,
            params={"competition_id": competition_id}
        )
        return response.status_code == 200
    
    def get_leaderboard(self, competition_id: str) -> List[Dict]:
        if not self.token:
            raise ValueError("Not logged in")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/competition/{competition_id}/leaderboard",
            headers=headers
        )
        return response.json() if response.status_code == 200 else []

    def on_market_update(self, callback: Callable[[MarketUpdate], None]):
        self.market_callback = callback

    async def connect_to_market_data(self, competition_id: str):
        if not self.token:
            raise ValueError("Not logged in")
            
        uri = f"{self.ws_base_url}/ws/{competition_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with websockets.connect(uri, extra_headers=headers) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if self.market_callback:
                        update = MarketUpdate(
                            prices=data["prices"],
                            leaderboard=data["leaderboard"]
                        )
                        self.market_callback(update)
                except Exception as e:
                    print(f"WebSocket error: {e}")
                    break 

    def get_orders(self, competition_id: str) -> List[dict]:
        if not self.token:
            raise ValueError("Not logged in")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/competition/{competition_id}/orders/{self.username}",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        return []

    def cancel_order(self, competition_id: str, order_id: str) -> bool:
        if not self.token:
            raise ValueError("Not logged in")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(
            f"{self.base_url}/competition/{competition_id}/order/{order_id}",
            headers=headers
        )
        return response.status_code == 200

    def get_orderbook_state(self, competition_id: str) -> dict:
        """Get current orderbook state including trades"""
        response = self.session.get(
            f"{self.base_url}/competition/{competition_id}/orderbook",
            headers=self._get_auth_headers()
        )
        if response.status_code == 200:
            return response.json()
        return {"buy_orders": [], "sell_orders": [], "trades": []}

    def _get_auth_headers(self) -> dict:
        if not self.token:
            raise ValueError("Not logged in")
        return {"Authorization": f"Bearer {self.token}"}