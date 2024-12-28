import numpy as np

class MarketSimulator:
    def __init__(self, initial_price: float, volatility: float):
        self.current_price = initial_price
        self.volatility = volatility
        
    def generate_next_price(self) -> float:
        # Simple random walk
        return self.current_price * np.exp(
            np.random.normal(0, self.volatility)
        )
