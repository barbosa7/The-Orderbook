import sys
import os
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import time
import threading
import requests
from typing import List, Dict
import logging
from datetime import datetime
from trading_client.client import TradingClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_bots.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('trading_bots')

class TradingBot:
    def __init__(self, username: str, password: str, api_url: str = "http://localhost:8000"):
        self.username = username
        self.password = password
        self.client = TradingClient(api_url)
        self.competition_id = "default_competition"
        self.running = False
        self.symbols = ["AAPL", "GOOGL"]
        self.last_order_cleanup = time.time()
        self.cleanup_interval = 60  # Cleanup orders every 60 seconds

    def start(self):
        if not self.client.login(self.username, self.password):
            return False
            
        if not self.client.join_competition(self.competition_id):
            return False
            
        return True

    def cleanup_orders(self):
        current_time = time.time()
        if current_time - self.last_order_cleanup < self.cleanup_interval:
            return

        try:
            orders = self.client.get_orders(self.competition_id)
            for order in orders:
                if self._should_cancel_order(order):
                    logger.info(f"Bot {self.username} cancelling order: {order['order_id']}")
                    self.client.cancel_order(self.competition_id, order['order_id'])
            
            self.last_order_cleanup = current_time
        except Exception as e:
            logger.error(f"Bot {self.username} failed to cleanup orders: {str(e)}")

    def _should_cancel_order(self, order: dict) -> bool:
        # Cancel orders that are more than 5 minutes old
        order_age = time.time() - order.get('timestamp', 0)
        return order_age > 300  # 5 minutes

    def would_self_trade(self, symbol: str, side: str, price: float) -> bool:
        try:
            orders = self.client.get_orders(self.competition_id)
            for order in orders:
                if order['symbol'] == symbol:
                    # If we're buying, check if we have any sell orders at or below our price
                    if side == "BUY" and order['side'] == "SELL" and order['price'] <= price:
                        return True
                    # If we're selling, check if we have any buy orders at or above our price
                    if side == "SELL" and order['side'] == "BUY" and order['price'] >= price:
                        return True
            return False
        except Exception as e:
            logger.error(f"Bot {self.username} failed to check self-trade: {str(e)}")
            return True  # Return True to be safe and prevent potential self-trades

    def place_order(self, symbol: str, side: str, quantity: int, price: float) -> bool:
        try:
            success = self.client.place_order(
                competition_id=self.competition_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price
            )
            if success:
                logger.info(f"Bot {self.username} placed {side} order: {quantity} {symbol} @ {price}")
            else:
                logger.error(f"Bot {self.username} failed to place {side} order: {quantity} {symbol} @ {price}")
            return success
        except Exception as e:
            logger.error(f"Bot {self.username} order failed with exception: {str(e)}")
            return False

class MarketMakerBot(TradingBot):
    def __init__(self, username: str, password: str, spread: float = 0.50):
        super().__init__(username, password)
        self.spread = spread
        self.last_trade_price = 100.0  # Initial reference price
        logger.info(f"Market Maker Bot {username} initialized with spread {spread}")
        
    def start(self):
        if not super().start():
            return
            
        self.running = True
        while self.running:
            try:
                # Get latest orderbook state to determine fair price
                orderbook = self.client.get_orderbook_state(self.competition_id)
                trades = orderbook.get('trades', [])
                
                # Update reference price based on recent trades
                if trades:
                    self.last_trade_price = trades[-1]['price']
                
                # Add some randomness to the fair price estimate
                fair_price = self.last_trade_price * (1 + random.uniform(-0.02, 0.02))
                
                for symbol in self.symbols:
                    bid_price = round(fair_price * (1 - self.spread/2), 2)
                    ask_price = round(fair_price * (1 + self.spread/2), 2)
                    
                    if not self.would_self_trade(symbol, "BUY", bid_price):
                        self.place_order(symbol, "BUY", random.randint(5, 20), bid_price)
                    if not self.would_self_trade(symbol, "SELL", ask_price):
                        self.place_order(symbol, "SELL", random.randint(5, 20), ask_price)
                    
            except Exception as e:
                logger.error(f"Market maker error: {str(e)}")
                
            time.sleep(2)

class NoiseTraderBot(TradingBot):
    def __init__(self, username: str, password: str):
        super().__init__(username, password)
        self.last_trade_price = 100.0
        self.price_view = random.uniform(0.8, 1.2)  # Random price bias
        self.view_update_time = time.time()
        
    def start(self):
        if not super().start():
            return
            
        self.running = True
        logger.info(f"Noise Trader Bot {self.username} started")
        
        while self.running:
            try:
                # Update price view every 30 seconds
                if time.time() - self.view_update_time > 30:
                    self.price_view = random.uniform(0.8, 1.2)
                    self.view_update_time = time.time()
                
                # Get latest market price
                orderbook = self.client.get_orderbook_state(self.competition_id)
                trades = orderbook.get('trades', [])
                if trades:
                    self.last_trade_price = trades[-1]['price']
                
                if random.random() < 0.4:  # Increased trading frequency
                    symbol = random.choice(self.symbols)
                    # Decide direction based on price view
                    if self.last_trade_price > (self.last_trade_price * self.price_view):
                        side = "SELL"  # Price is above our view, sell
                    else:
                        side = "BUY"   # Price is below our view, buy
                        
                    # Add aggressive price adjustment
                    price_adjustment = random.uniform(-0.05, 0.05)
                    price = round(self.last_trade_price * (1 + price_adjustment), 2)
                    
                    if not self.would_self_trade(symbol, side, price):
                        quantity = random.randint(10, 100)  # Larger order sizes
                        self.place_order(symbol, side, quantity, price)
                
            except Exception as e:
                logger.error(f"Noise trader error: {str(e)}")
                
            time.sleep(random.uniform(1, 3))
