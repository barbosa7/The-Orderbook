from trading_bots import MarketMakerBot, NoiseTraderBot
import threading

def main():
    # Create and start market maker
    mm_bot = MarketMakerBot("trader1", "pass123", spread=0.10)
    mm_thread = threading.Thread(target=mm_bot.start)
    mm_thread.daemon = True
    mm_thread.start()
    
    # Create and start noise trader
    noise_bot = NoiseTraderBot("trader2", "pass456")
    noise_thread = threading.Thread(target=noise_bot.start)
    noise_thread.daemon = True
    noise_thread.start()
    

    mm_bot = MarketMakerBot("trader3", "pass456", spread=0.10)
    mm_thread = threading.Thread(target=mm_bot.start)
    mm_thread.daemon = True
    mm_thread.start()
    
    # Create and start noise trader
    noise_bot = NoiseTraderBot("trader4", "pass456")
    noise_thread = threading.Thread(target=noise_bot.start)
    noise_thread.daemon = True
    noise_thread.start()
    
    try:
        while True:
            pass  # Keep main thread alive
    except KeyboardInterrupt:
        print("Shutting down bots...")
        mm_bot.running = False
        noise_bot.running = False

if __name__ == "__main__":
    main() 