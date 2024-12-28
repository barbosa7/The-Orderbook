import asyncio
from client import TradingClient

async def main():
    # Initialize client
    client = TradingClient("http://localhost:8000")
    
    # Login
    if not client.login("trader1", "pass123"):
        print("Login failed")
        return
        
    # Join competition
    competition_id = "your_competition_id"
    if not client.join_competition(competition_id):
        print("Failed to join competition")
        return

    # Define market update callback
    def on_market_update(update):
        # Simple market making strategy
        for symbol, price in update.prices.items():
            # Place buy order slightly below market
            client.place_order(
                competition_id=competition_id,
                symbol=symbol,
                side="BUY",
                quantity=100,
                price=price * 0.999
            )
            
            # Place sell order slightly above market
            client.place_order(
                competition_id=competition_id,
                symbol=symbol,
                side="SELL",
                quantity=100,
                price=price * 1.001
            )
            
        # Print current leaderboard
        print("\nLeaderboard:")
        for entry in update.leaderboard:
            print(f"{entry['name']}: {entry['pnl']:.2f}")

    # Register callback and connect to market data
    client.on_market_update(on_market_update)
    await client.connect_to_market_data(competition_id)

if __name__ == "__main__":
    asyncio.run(main())
