from surmount.base_class import Strategy, TargetAllocation
from surmount.data import OHLCV
from surmount.technical_indicators import SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "BBAI"
        # Considering OHLCV is automatically included, no need to manually add to data_list
        self.low_sma_period = 200
        self.high_sma_period = 200

    @property
    def assets(self):
        return [self.ticker]

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        # Calculate 200-day SMA for both low and high prices
        low_prices = [i[self.ticker]['low'] for i in data['ohlcv']]
        high_prices = [i[self.ticker]['high'] for i in data['ohlcv']]
        current_price = data['ohlcv'][-1][self.ticker]['close']
        
        low_sma = SMA(self.ticker, [{'close': lp} for lp in low_prices], self.low_sma_period)
        high_sma = SMA(self.ticker, [{'close': hp} for hp in high_prices], self.high_sma_period)
    
        if len(low_sma) == 0 or len(high_sma) == 0:
            log('SMA calculation failed or insufficient data')
            return TargetAllocation({self.ticker: 0})
        
        # Determine if current price is within 15% of the 200-day moving low average
        if current_price <= low_sma[-1] * 1.15:
            allocation = 1  # Buy / Hold (allocate 100% of portfolio)
        # Determine if current price is within 30% of the 200-day moving high average
        elif current_price >= high_sma[-1] * 0.70:
            allocation = 0  # Sell / Not Hold
        else:
            # Maintain current position if neither condition is met
            allocation = data['holdings'].get(self.ticker, 0)

        return TargetAllocation({self.ticker: allocation})