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


@dataclass
class Competition:
    competition_id: str
    name: str
    start_time: float
    end_time: float
    order_book: OrderBook = field(default_factory=OrderBook)
    participants: Dict[str, Dict] = field(default_factory=dict)
    orders: List[Order] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)
    instruments: Dict[str, Instrument] = field(default_factory=dict)

    def is_active(self) -> bool:
        return time.time() < self.end_time

    def add_participant(self, user_id: str, display_name: str) -> bool:
        if user_id not in self.participants:
            self.participants[user_id] = {
                "cash": 1000000.0,
                "display_name": display_name,
                "positions": {}
            }
            return True
        return False

    def add_instrument(self, instrument: Instrument):
        self.instruments[instrument.symbol] = instrument

class CompetitionManager:
    def __init__(self):
        self.active_competitions: Dict[str, Competition] = {}
        self.max_participants = 30
        
    def create_default_competition(self) -> Competition:
        competition = Competition(
            competition_id="default_competition",
            name="Default Competition",
            start_time=time.time(),
            end_time=time.time() + (60 * 60)  # 1 hour
        )
        
        for symbol in ["AAPL", "GOOGL"]:
            competition.add_instrument(Instrument(
                symbol=symbol,
                initial_price=100.0,
                tick_size=0.01,
                lot_size=1,
                volatility=0.1
            ))
        
        self.active_competitions["default_competition"] = competition
        return competition
        
    def add_participant(self, competition_id: str, user_id: str, display_name: str) -> bool:
        competition = self.active_competitions.get(competition_id)
        if not competition:
            if competition_id == "default_competition":
                self.create_default_competition()
                competition = self.active_competitions["default_competition"]
            else:
                raise ValueError("Competition not found")
                
        return competition.add_participant(user_id, display_name)
        
    def get_leaderboard(self, competition_id: str) -> List[Dict]:
        competition = self.active_competitions[competition_id]
        current_prices = self._get_current_prices(competition)
        
        rankings = []
        for participant in competition.participants.values():
            rankings.append({
                'name': participant.name,
                'pnl': participant.get_pnl(current_prices),
            })
            
        return sorted(rankings, key=lambda x: x['pnl'], reverse=True)
