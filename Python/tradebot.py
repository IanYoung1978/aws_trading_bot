import time
import ccxt
import logging
import numpy as np

# Logging Configuration
logging.basicConfig(filename="trading_bot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

class TradingBot:
    def __init__(self, api_key, api_secret, symbol, risk_percent, stop_loss_percent, cooldown_period):
        self.exchange = ccxt.kraken({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self.symbol = symbol
        self.risk_percent = risk_percent
        self.stop_loss_percent = stop_loss_percent
        self.cooldown_period = cooldown_period  # Seconds
        self.last_trade_time = 0
        self.trailing_sell_price = None
        self.trailing_buy_price = None

    def fetch_historical_data(self, timeframe="1h", limit=100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logging.error(f"Error fetching historical data: {e}")
            raise

    def calculate_bollinger_bands(self, data, period=20, std_dev_factor=2):
        closes = [x[4] for x in data]
        ma = np.mean(closes[-period:])
        std_dev = np.std(closes[-period:])
        return ma + std_dev_factor * std_dev, ma - std_dev_factor * std_dev

    def calculate_keltner_channels(self, data, period=20, multiplier=1.5):
        highs = [x[2] for x in data]
        lows = [x[3] for x in data]
        closes = [x[4] for x in data]
        ma = np.mean(closes[-period:])
        atr = np.mean([highs[i] - lows[i] for i in range(-period, 0)])
        return ma + multiplier * atr, ma - multiplier * atr

    def calculate_volatility(self, data, period=20):
        closes = [x[4] for x in data]
        changes = [abs(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]
        return np.mean(changes[-period:])

    def get_account_balances(self):
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            logging.error(f"Error fetching account balances: {e}")
            raise

    def place_order(self, side, amount):
        try:
            if side == "buy":
                return self.exchange.create_market_buy_order(self.symbol, amount)
            elif side == "sell":
                return self.exchange.create_market_sell_order(self.symbol, amount)
        except Exception as e:
            logging.error(f"Error placing {side} order: {e}")
            raise

    def execute_strategy(self):
        try:
            data = self.fetch_historical_data()
            volatility = self.calculate_volatility(data)
            upper, lower = (self.calculate_bollinger_bands(data) if volatility > 0.02 else self.calculate_keltner_channels(data))
            balances = self.get_account_balances()
            current_price = data[-1][4]

            base_currency, quote_currency = self.symbol.split("/")
            base_balance = balances['free'][base_currency]
            quote_balance = balances['free'][quote_currency]

            # Risk-Adjusted Trade Sizes
            max_trade_amount = self.risk_percent * quote_balance / 100

            if current_price >= upper:
                # Check trailing sell
                if self.trailing_sell_price and current_price < self.trailing_sell_price:
                    logging.info("Trailing sell executed.")
                    self.place_order("sell", base_balance)
                    self.trailing_sell_price = None
                elif not self.trailing_sell_price:
                    logging.info("Price hit upper band, initiating trailing sell.")
                    self.trailing_sell_price = current_price * (1 - 0.03)  # 3% trailing margin

            elif current_price <= lower:
                # Check trailing buy
                if self.trailing_buy_price and current_price > self.trailing_buy_price:
                    logging.info("Trailing buy executed.")
                    self.place_order("buy", max_trade_amount / current_price)
                    self.trailing_buy_price = None
                elif not self.trailing_buy_price:
                    logging.info("Price hit lower band, initiating trailing buy.")
                    self.trailing_buy_price = current_price * (1 + 0.03)  # 3% trailing margin

        except Exception as e:
            logging.error(f"Error in strategy execution: {e}")

# Configuration
bot = TradingBot(
    api_key="your_api_key",
    api_secret="your_api_secret",
    symbol="BTC/USD",
    risk_percent=5,  # 5% of account balance per trade
    stop_loss_percent=10,  # 10% stop-loss
    cooldown_period=3600  # 1 hour cooldown
)

# Main Loop
while True:
    bot.execute_strategy()
    time.sleep(60)  # Run every minute
