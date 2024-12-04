import pytest
from bot import TradeBot

def test_bot_initialization():
    bot = TradeBot(mock=True)
    assert bot.mock is True

def test_trade_execution_mock():
    bot = TradeBot(mock=True)
    # Mock test for trade execution
    bot.execute_trade("buy", "XBTUSD", "0.01")
    bot.execute_trade("sell", "XBTUSD", "0.01")
