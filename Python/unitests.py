import unittest
import tradebot

class TestTradingBot(unittest.TestCase):
    def setUp(self):
        self.bot = tradebot.TradingBot(api_key="dummy", api_secret="dummy", symbol="BTC/USD", risk_percent=5, stop_loss_percent=10, cooldown_period=3600)

    def test_bollinger_bands(self):
        data = [[0, 0, 0, 0, i] for i in range(1, 21)]
        upper, lower = self.bot.calculate_bollinger_bands(data)
        self.assertTrue(upper > lower)

    def test_keltner_channels(self):
        data = [[0, 0, 2, 1, 1.5] for _ in range(20)]
        upper, lower = self.bot.calculate_keltner_channels(data)
        self.assertTrue(upper > lower)

    def test_volatility(self):
        data = [[0, 0, 0, 0, i] for i in range(1, 21)]
        volatility = self.bot.calculate_volatility(data)
        self.assertTrue(volatility > 0)

if __name__ == "__main__":
    unittest.main()
