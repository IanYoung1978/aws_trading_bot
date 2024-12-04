import pytest
from indicators import calculate_indicators

def test_calculate_indicators():
    # Sample data for testing
    sample_data = [
        [0, 50000, 50500, 49500, 50000, 100], 
        [1, 50000, 50700, 49600, 50100, 150],
        [2, 50100, 50900, 50000, 50200, 120],
    ]

    indicators = calculate_indicators(sample_data)
    assert 'bollinger' in indicators
    assert 'keltner' in indicators
    assert 'volatility' in indicators
    assert 'rsi' in indicators
