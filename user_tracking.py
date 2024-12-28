from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import uuid
import time

@dataclass
class Instrument:
    symbol: str
    initial_price: float
    tick_size: float
    lot_size: int
    volatility: float  # For price simulation

class CompetitionConfig:
    def __init__(self, name: str, duration_minutes: int):
        self.id = str(uuid.uuid4())
        self.name = name
        self.duration_minutes = duration_minutes
        self.instruments: Dict[str, Instrument] = {}
        self.start_time: Optional[float] = None
        self.participants: Dict[str, 'Participant'] = {}
        
    def add_instrument(self, instrument: Instrument):
        self.instruments[instrument.symbol] = instrument
        
    def is_active(self) -> bool:
        if not self.start_time:
            return False
        return time.time() < self.start_time + (self.duration_minutes * 60)

@dataclass
class Position:
    quantity: int = 0
    average_price: float = 0.0
    realized_pnl: float = 0.0
    
    def update(self, trade_qty: int, trade_price: float):
        if self.quantity == 0:
            self.average_price = trade_price
        else:
            self.average_price = (
                (self.quantity * self.average_price + trade_qty * trade_price) / 
                (self.quantity + trade_qty)
            )
        self.quantity += trade_qty

class Participant:
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name
        self.positions: Dict[str, Position] = {}
        self.cash = 0.0
        
    def get_pnl(self, current_prices: Dict[str, float]) -> float:
        total_pnl = 0.0
        for symbol, position in self.positions.items():
            if position.quantity != 0:
                unrealized_pnl = (
                    position.quantity * 
                    (current_prices[symbol] - position.average_price)
                )
                total_pnl += unrealized_pnl + position.realized_pnl
        return total_pnl
