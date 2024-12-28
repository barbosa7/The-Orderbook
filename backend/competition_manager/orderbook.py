from typing import List
import logging
from .models import Order, Trade, OrderSide

# Configure logging
logger = logging.getLogger('orderbook')
logger.setLevel(logging.DEBUG)

class OrderBook:
    def __init__(self):
        self.buy_orders: List[Order] = []
        self.sell_orders: List[Order] = []
        self.trades: List[Trade] = []
        
    def _log_orderbook_state(self):
        logger.debug("Current OrderBook State:")
        logger.debug("Buy Orders:")
        for order in self.buy_orders:
            logger.debug(f"  Price: {order.price}, Qty: {order.quantity - order.filled_quantity}, User: {order.user_id}")
        logger.debug("Sell Orders:")
        for order in self.sell_orders:
            logger.debug(f"  Price: {order.price}, Qty: {order.quantity - order.filled_quantity}, User: {order.user_id}")
            
    def add_order(self, order: Order) -> List[Trade]:
        logger.debug(f"Adding new order: {order.side} {order.quantity}@{order.price} from {order.user_id}")
        trades = []
        if order.side == OrderSide.BUY:
            trades = self._match_buy_order(order)
        else:
            trades = self._match_sell_order(order)
        self._log_orderbook_state()
        return trades
            
    def _match_buy_order(self, buy_order: Order) -> List[Trade]:
        trades = []
        self.sell_orders.sort(key=lambda x: (x.price, x.timestamp))
        
        while self.sell_orders and buy_order.filled_quantity < buy_order.quantity:
            sell_order = self.sell_orders[0]
            
            # Skip if it would be a self-trade
            if sell_order.user_id == buy_order.user_id:
                self.sell_orders.pop(0)
                continue
            
            if sell_order.price > buy_order.price:
                break
                
            trade_quantity = min(
                buy_order.quantity - buy_order.filled_quantity,
                sell_order.quantity - sell_order.filled_quantity
            )
            
            trade = Trade(
                order_id=buy_order.order_id,
                counter_order_id=sell_order.order_id,
                price=sell_order.price,
                quantity=trade_quantity
            )
            
            trades.append(trade)
            buy_order.filled_quantity += trade_quantity
            sell_order.filled_quantity += trade_quantity
            
            if sell_order.filled_quantity == sell_order.quantity:
                self.sell_orders.pop(0)
                
        if buy_order.filled_quantity < buy_order.quantity:
            self.buy_orders.append(buy_order)
            
        return trades
        
    def _match_sell_order(self, sell_order: Order) -> List[Trade]:
        trades = []
        self.buy_orders.sort(key=lambda x: (-x.price, x.timestamp))
        
        while self.buy_orders and sell_order.filled_quantity < sell_order.quantity:
            buy_order = self.buy_orders[0]
            
            # Skip if it would be a self-trade
            if buy_order.user_id == sell_order.user_id:
                self.buy_orders.pop(0)
                continue
            
            if buy_order.price < sell_order.price:
                break
                
            trade_quantity = min(
                sell_order.quantity - sell_order.filled_quantity,
                buy_order.quantity - buy_order.filled_quantity
            )
            
            trade = Trade(
                order_id=sell_order.order_id,
                counter_order_id=buy_order.order_id,
                price=buy_order.price,
                quantity=trade_quantity
            )
            
            trades.append(trade)
            sell_order.filled_quantity += trade_quantity
            buy_order.filled_quantity += trade_quantity
            
            if buy_order.filled_quantity == buy_order.quantity:
                self.buy_orders.pop(0)
                
        if sell_order.filled_quantity < sell_order.quantity:
            self.sell_orders.append(sell_order)
            
        return trades
        
    def cancel_order(self, order_id: str, user_id: str) -> bool:
        """Cancel an order if it exists and belongs to the user."""
        for orders in [self.buy_orders, self.sell_orders]:
            for i, order in enumerate(orders):
                if order.order_id == order_id and order.user_id == user_id:
                    orders.pop(i)
                    logger.info(f"Order {order_id} cancelled by user {user_id}")
                    return True
        return False