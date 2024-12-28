from dataclasses import dataclass
from typing import List, Dict
from enum import Enum
import time

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Order:
    id: str
    user_id: str
    instrument: str
    side: OrderSide
    price: float
    quantity: int
    timestamp: float

class OrderBook:
    def __init__(self, instrument: str):
        self.instrument = instrument
        self.bids: List[Order] = []  # Buy orders
        self.asks: List[Order] = []  # Sell orders
        
    def add_order(self, order: Order) -> List[Order]:
        """Add order to book and return list of matched trades"""
        if order.side == OrderSide.BUY:
            return self._match_buy_order(order)
        return self._match_sell_order(order)
    
    def _match_buy_order(self, buy_order: Order) -> List[Order]:
        matches = []
        remaining_quantity = buy_order.quantity
        
        # Match against existing sell orders
        while remaining_quantity > 0 and self.asks:
            best_ask = self.asks[0]
            if best_ask.price > buy_order.price:
                break
                
            match_quantity = min(remaining_quantity, best_ask.quantity)
            matches.append(Order(
                id=f"trade_{time.time()}",
                user_id=best_ask.user_id,
                instrument=self.instrument,
                side=OrderSide.SELL,
                price=best_ask.price,
                quantity=match_quantity,
                timestamp=time.time()
            ))
            
            remaining_quantity -= match_quantity
            best_ask.quantity -= match_quantity
            
            if best_ask.quantity == 0:
                self.asks.pop(0)
                
        # Add remaining order to book
        if remaining_quantity > 0:
            buy_order.quantity = remaining_quantity
            self._insert_buy_order(buy_order)
            
        return matches

    def _insert_buy_order(self, order: Order):
        """Insert buy order maintaining price-time priority"""
        insert_idx = 0
        for idx, existing_order in enumerate(self.bids):
            if order.price < existing_order.price:
                insert_idx = idx + 1
            else:
                break
        self.bids.insert(insert_idx, order)
