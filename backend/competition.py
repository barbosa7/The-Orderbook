from dataclasses import dataclass, field
from typing import Dict, List
from .models import Order, Trade
from .orderbook import OrderBook
import time

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

    def process_trades(self, trades: List[Trade]):
        for trade in trades:
            self.trades.append(trade)
            
            buyer_id = trade.counter_order_id.split('_')[0]
            seller_id = trade.order_id.split('_')[0]
            
            if buyer_id in self.participants and seller_id in self.participants:
                trade_value = trade.price * trade.quantity
                
                self.participants[buyer_id]["cash"] -= trade_value
                self.participants[seller_id]["cash"] += trade_value
                
                buyer_positions = self.participants[buyer_id].setdefault("positions", {})
                seller_positions = self.participants[seller_id].setdefault("positions", {})
                
                buyer_positions[trade.symbol] = buyer_positions.get(trade.symbol, 0) + trade.quantity
                seller_positions[trade.symbol] = seller_positions.get(trade.symbol, 0) - trade.quantity

    def get_participant_pnl(self, user_id: str) -> float:
        if user_id not in self.participants:
            return 0.0
            
        participant = self.participants[user_id]
        total_value = participant["cash"]
        
        for symbol, quantity in participant.get("positions", {}).items():
            latest_price = self._get_latest_price(symbol)
            total_value += quantity * latest_price
            
        return total_value - 1000000.0

    def _get_latest_price(self, symbol: str) -> float:
        recent_trades = [t for t in self.trades if t.symbol == symbol]
        if recent_trades:
            return recent_trades[-1].price
            
        buy_orders = [o for o in self.order_book.buy_orders if o.symbol == symbol]
        sell_orders = [o for o in self.order_book.sell_orders if o.symbol == symbol]
        
        if buy_orders and sell_orders:
            return (buy_orders[0].price + sell_orders[0].price) / 2
        
        return 100.0

    def get_order_book_state(self):
        return {
            "buy_orders": [
                {
                    "price": order.price,
                    "quantity": order.quantity - order.filled_quantity,
                    "user_id": order.user_id
                }
                for order in self.order_book.buy_orders
            ],
            "sell_orders": [
                {
                    "price": order.price,
                    "quantity": order.quantity - order.filled_quantity,
                    "user_id": order.user_id
                }
                for order in self.order_book.sell_orders
            ],
            "trades": [
                {
                    "price": trade.price,
                    "quantity": trade.quantity,
                    "buyer_id": trade.counter_order_id.split('_')[0],
                    "seller_id": trade.order_id.split('_')[0]
                }
                for trade in self.trades[-10:]
            ]
        }