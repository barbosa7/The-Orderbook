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
