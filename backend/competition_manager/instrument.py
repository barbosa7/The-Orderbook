from dataclasses import dataclass

@dataclass
class Instrument:
    symbol: str
    initial_price: float
    tick_size: float
    lot_size: int
    volatility: float 