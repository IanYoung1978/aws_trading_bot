const ccxt = require('ccxt');
const { TradingBot } = require('./tradingBot'); // Assume the bot is in `tradingBot.js`

jest.mock('ccxt'); // Mock the ccxt library

describe('TradingBot', () => {
  let bot;

  beforeEach(() => {
    // Mock API keys and initialize bot
    bot = new TradingBot('test-api-key', 'test-api-secret', 'BTC/USD', 5, 10, 3600000);

    // Mock the ccxt exchange methods
    bot.exchange.fetchOHLCV = jest.fn();
    bot.exchange.fetchBalance = jest.fn();
    bot.exchange.createMarketBuyOrder = jest.fn();
    bot.exchange.createMarketSellOrder = jest.fn();
  });

  test('fetchHistoricalData should fetch OHLCV data', async () => {
    // Mock response
    const mockData = [
      [1633065600000, 42000, 42500, 41800, 42400, 1000],
      [1633069200000, 42400, 42600, 42300, 42500, 1500],
    ];
    bot.exchange.fetchOHLCV.mockResolvedValue(mockData);

    const data = await bot.fetchHistoricalData('1h', 2);

    expect(bot.exchange.fetchOHLCV).toHaveBeenCalledWith('BTC/USD', '1h', undefined, 2);
    expect(data).toEqual(mockData);
  });

  test('calculateBollingerBands should calculate correct bands', () => {
    const mockData = [
      [1633065600000, 42000, 42500, 41800, 42000, 1000],
      [1633069200000, 42000, 42500, 41800, 42200, 1500],
      [1633072800000, 42000, 42500, 41800, 42100, 2000],
      [1633076400000, 42000, 42500, 41800, 42400, 1800],
      [1633080000000, 42000, 42500, 41800, 42300, 1100],
    ];
    const result = bot.calculateBollingerBands(mockData, 5, 2);

    expect(result).toHaveProperty('upper');
    expect(result).toHaveProperty('lower');
    expect(result.upper).toBeGreaterThan(result.lower);
  });

  test('calculateKeltnerChannels should calculate correct channels', () => {
    const mockData = [
      [1633065600000, 42000, 42500, 41800, 42000, 1000],
      [1633069200000, 42000, 42500, 41800, 42200, 1500],
      [1633072800000, 42000, 42500, 41800, 42100, 2000],
      [1633076400000, 42000, 42500, 41800, 42400, 1800],
      [1633080000000, 42000, 42500, 41800, 42300, 1100],
    ];
    const result = bot.calculateKeltnerChannels(mockData, 5, 1.5);

    expect(result).toHaveProperty('upper');
    expect(result).toHaveProperty('lower');
    expect(result.upper).toBeGreaterThan(result.lower);
  });

  test('getAccountBalances should fetch balances', async () => {
    const mockBalances = {
      free: { BTC: 0.1, USD: 1000 },
      used: { BTC: 0.05, USD: 500 },
    };
    bot.exchange.fetchBalance.mockResolvedValue(mockBalances);

    const balances = await bot.getAccountBalances();

    expect(bot.exchange.fetchBalance).toHaveBeenCalled();
    expect(balances).toEqual(mockBalances);
  });

  test('placeOrder should call the correct exchange method', async () => {
    bot.exchange.createMarketBuyOrder.mockResolvedValue({ id: 'test-buy' });
    bot.exchange.createMarketSellOrder.mockResolvedValue({ id: 'test-sell' });

    const buyResult = await bot.placeOrder('buy', 0.01);
    expect(bot.exchange.createMarketBuyOrder).toHaveBeenCalledWith('BTC/USD', 0.01);
    expect(buyResult).toEqual({ id: 'test-buy' });

    const sellResult = await bot.placeOrder('sell', 0.01);
    expect(bot.exchange.createMarketSellOrder).toHaveBeenCalledWith('BTC/USD', 0.01);
    expect(sellResult).toEqual({ id: 'test-sell' });
  });

  test('executeStrategy should handle trailing buy and sell', async () => {
    const mockData = [
      [1633065600000, 42000, 42500, 41800, 42000, 1000],
      [1633069200000, 42000, 42500, 41800, 42200, 1500],
      [1633072800000, 42000, 42500, 41800, 42100, 2000],
      [1633076400000, 42000, 42500, 41800, 42400, 1800],
      [1633080000000, 42000, 42500, 41800, 42300, 1100],
    ];
    bot.exchange.fetchOHLCV.mockResolvedValue(mockData);
    bot.exchange.fetchBalance.mockResolvedValue({
      free: { BTC: 0.1, USD: 1000 },
      used: { BTC: 0.05, USD: 500 },
    });

    await bot.executeStrategy();

    expect(bot.exchange.fetchOHLCV).toHaveBeenCalled();
    expect(bot.exchange.fetchBalance).toHaveBeenCalled();
  });
});
