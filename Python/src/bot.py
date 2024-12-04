import argparse
import time
from indicators import calculate_indicators
from notifier import send_email
from logger import log_trade
from krakenex import API

class TradeBot:
    def __init__(self, mock=False):
        self.mock = mock
        self.api = API()
        self.api_key = config.KRAKEN_API_KEY
        self.private_key = config.KRAKEN_PRIVATE_KEY
        self.last_buy_price = None
        self.last_sell_price = None

    def fetch_market_data(self, pair):
        # Fetch OHLC data from Kraken API
        response = self.api.query_public('OHLC', {'pair': pair, 'interval': 1})
        if 'error' in response and response['error']:
            raise Exception("Kraken API Error: " + str(response['error']))
        return response['result'][pair]

    def execute_trade(self, action, pair, amount):
        if self.mock:
            print(f"MOCK: Would have executed {action} on {pair} for {amount}")
            return

        if action == "buy":
            self.api.query_private('AddOrder', {
                'pair': pair, 'type': 'buy', 'ordertype': 'market', 'volume': amount
            })
        elif action == "sell":
            self.api.query_private('AddOrder', {
                'pair': pair, 'type': 'sell', 'ordertype': 'market', 'volume': amount
            })

    def run(self, pair):
        while True:
            try:
                # Fetch data and calculate indicators
                data = self.fetch_market_data(pair)
                indicators = calculate_indicators(data)

                # Decision-making logic
                if indicators['volatility'] > config.X_PERCENT:
                    bounds = indicators['keltner']
                else:
                    bounds = indicators['bollinger']

                current_price = data[-1][4]
                if current_price > bounds['upper'] and not self.last_sell_price:
                    self.execute_trade("sell", pair, "all")
                    self.last_sell_price = current_price
                    self.last_buy_price = None
                    log_trade("sell", current_price)

                elif current_price < bounds['lower'] and not self.last_buy_price:
                    self.execute_trade("buy", pair, "all")
                    self.last_buy_price = current_price
                    self.last_sell_price = None
                    log_trade("buy", current_price)

                # Advanced functionality checks here...

            except Exception as e:
                print(f"Error: {e}")
                send_email("Trade Bot Error", str(e))

            time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the trade bot.")
    parser.add_argument('--mock', action='store_true', help="Run in mock mode")
    args = parser.parse_args()

    bot = TradeBot(mock=args.mock)
    bot.run("XBTUSD")
