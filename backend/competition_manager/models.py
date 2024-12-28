from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Order:
    competition_id: str
    user_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    order_id: str
    filled_quantity: int = 0
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "price": self.price,
            "quantity": self.quantity,
            "filled_quantity": self.filled_quantity,
            "timestamp": self.timestamp
        }

@dataclass
class Trade:
    order_id: str
    counter_order_id: str
    price: float
    quantity: int
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp() 