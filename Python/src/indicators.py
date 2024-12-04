import numpy as np
import pandas as pd

def calculate_indicators(data):
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume"])
    df['close'] = df['close'].astype(float)

    # Bollinger Bands
    df['20sma'] = df['close'].rolling(window=20).mean()
    df['stddev'] = df['close'].rolling(window=20).std()
    df['bollinger_upper'] = df['20sma'] + 2 * df['stddev']
    df['bollinger_lower'] = df['20sma'] - 2 * df['stddev']

    # Keltner Channels
    df['atr'] = (df['high'] - df['low']).rolling(window=10).mean()
    df['keltner_upper'] = df['20sma'] + 2 * df['atr']
    df['keltner_lower'] = df['20sma'] - 2 * df['atr']

    # Volatility
    df['volatility'] = (df['high'] - df['low']) / df['close'] * 100

    # RSI
    df['change'] = df['close'].diff()
    df['gain'] = np.where(df['change'] > 0, df['change'], 0)
    df['loss'] = np.where(df['change'] < 0, -df['change'], 0)
    avg_gain = df['gain'].rolling(window=14).mean()
    avg_loss = df['loss'].rolling(window=14).mean()
    df['rs'] = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + df['rs']))

    return {
        'bollinger': {'upper': df['bollinger_upper'].iloc[-1], 'lower': df['bollinger_lower'].iloc[-1]},
        'keltner': {'upper': df['keltner_upper'].iloc[-1], 'lower': df['keltner_lower'].iloc[-1]},
        'volatility': df['volatility'].iloc[-1],
        'rsi': df['rsi'].iloc[-1],
    }
