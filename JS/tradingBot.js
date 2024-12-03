const ccxt = require('ccxt');
const nodemailer = require('nodemailer');

class TradingBot {
  constructor(apiKey, apiSecret, symbol, riskPercent, stopLossPercent, cooldownPeriod) {
    this.exchange = new ccxt.kraken({
      apiKey: apiKey,
      secret: apiSecret,
    });
    this.symbol = symbol;
    this.riskPercent = riskPercent;
    this.stopLossPercent = stopLossPercent;
    this.cooldownPeriod = cooldownPeriod; // In milliseconds
    this.lastTradeTime = 0;
    this.trailingSellPrice = null;
    this.trailingBuyPrice = null;
  }

  async fetchHistoricalData(timeframe = '1h', limit = 100) {
    try {
      const ohlcv = await this.exchange.fetchOHLCV(this.symbol, timeframe, undefined, limit);
      return ohlcv;
    } catch (error) {
      console.error(`Error fetching historical data: ${error.message}`);
      throw error;
    }
  }

  calculateBollingerBands(data, period = 20, stdDevFactor = 2) {
    const closes = data.map(candle => candle[4]);
    const slice = closes.slice(-period);
    const mean = slice.reduce((a, b) => a + b, 0) / period;
    const stdDev = Math.sqrt(slice.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b, 0) / period);
    return {
      upper: mean + stdDevFactor * stdDev,
      lower: mean - stdDevFactor * stdDev,
    };
  }

  calculateKeltnerChannels(data, period = 20, multiplier = 1.5) {
    const highs = data.map(candle => candle[2]);
    const lows = data.map(candle => candle[3]);
    const closes = data.map(candle => candle[4]);
    const slice = closes.slice(-period);
    const ma = slice.reduce((a, b) => a + b, 0) / period;
    const atr = highs
      .map((high, i) => high - lows[i])
      .slice(-period)
      .reduce((a, b) => a + b, 0) / period;
    return {
      upper: ma + multiplier * atr,
      lower: ma - multiplier * atr,
    };
  }

  async getAccountBalances() {
    try {
      return await this.exchange.fetchBalance();
    } catch (error) {
      console.error(`Error fetching account balances: ${error.message}`);
      throw error;
    }
  }

  async placeOrder(side, amount) {
    try {
      if (side === 'buy') {
        return await this.exchange.createMarketBuyOrder(this.symbol, amount);
      } else if (side === 'sell') {
        return await this.exchange.createMarketSellOrder(this.symbol, amount);
      }
    } catch (error) {
      console.error(`Error placing ${side} order: ${error.message}`);
      throw error;
    }
  }

  async executeStrategy() {
    try {
      const data = await this.fetchHistoricalData();
      const volatility = this.calculateVolatility(data);
      const { upper, lower } = volatility > 0.02
        ? this.calculateBollingerBands(data)
        : this.calculateKeltnerChannels(data);
      const balances = await this.getAccountBalances();
      const currentPrice = data[data.length - 1][4];

      const [baseCurrency, quoteCurrency] = this.symbol.split('/');
      const baseBalance = balances.free[baseCurrency] || 0;
      const quoteBalance = balances.free[quoteCurrency] || 0;
      const maxTradeAmount = (this.riskPercent / 100) * quoteBalance;

      if (currentPrice >= upper) {
        if (this.trailingSellPrice && currentPrice < this.trailingSellPrice) {
          console.info('Trailing sell triggered.');
          await this.placeOrder('sell', baseBalance);
          this.trailingSellPrice = null;
        } else if (!this.trailingSellPrice) {
          console.info('Price hit upper band, initiating trailing sell.');
          this.trailingSellPrice = currentPrice * (1 - 0.03); // 3% trailing margin
        }
      } else if (currentPrice <= lower) {
        if (this.trailingBuyPrice && currentPrice > this.trailingBuyPrice) {
          console.info('Trailing buy triggered.');
          await this.placeOrder('buy', maxTradeAmount / currentPrice);
          this.trailingBuyPrice = null;
        } else if (!this.trailingBuyPrice) {
          console.info('Price hit lower band, initiating trailing buy.');
          this.trailingBuyPrice = currentPrice * (1 + 0.03); // 3% trailing margin
        }
      }
    } catch (error) {
      console.error(`Error executing strategy: ${error.message}`);
    }
  }

  calculateVolatility(data, period = 20) {
    const closes = data.map(candle => candle[4]);
    const changes = closes.slice(1).map((close, i) => Math.abs(close - closes[i]) / closes[i]);
    return changes.slice(-period).reduce((a, b) => a + b, 0) / period;
  }
}

// Email Notifications (for completed trades and errors)
function sendEmail(subject, message) {
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: 'your-email@gmail.com',
      pass: 'your-email-password',
    },
  });

  const mailOptions = {
    from: 'your-email@gmail.com',
    to: 'your-email@gmail.com',
    subject: subject,
    text: message,
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      console.error(`Error sending email: ${error.message}`);
    } else {
      console.info(`Email sent: ${info.response}`);
    }
  });
}

// Configuration
const bot = new TradingBot(
  'your-api-key',
  'your-api-secret',
  'BTC/USD',
  5,  // Risk percent
  10, // Stop-loss percent
  3600000 // Cooldown period in milliseconds (1 hour)
);

// Main Loop
setInterval(async () => {
  await bot.executeStrategy();
}, 60000); // Run every minute
