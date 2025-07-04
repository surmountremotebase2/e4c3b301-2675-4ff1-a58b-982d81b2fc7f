from surmount.base_class import Strategy, TargetAllocation
from surmount.data import OHLCV, Asset
from surmount.technical_indicators import SMA
import numpy as np

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["SMCI"]
        # We want to analyze daily price data
        self.lookback_period = 200
        self.buy_threshold = 1.20  # Adjusted for Surmount compatibility
        self.sell_threshold = 0.70  # Adjusted for Surmount compatibility
        self.qty = 1  # Quantity to trade, not used directly in Surmount

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"

    @property
    def data(self):
        return [OHLCV(ticker, self.lookback_period + 5) for ticker in self.tickers]

    def run(self, data):
        allocation = {}
        for ticker in self.tickers:
            ohlcv_data = data["ohlcv"][ticker]
            close_prices = np.array([day["close"] for day in ohlcv_data])
            if close_prices.size >= self.lookback_period:
                current_price = close_prices[-1]
                low_200 = close_prices[-self.lookback_period:].min()
                high_200 = close_prices[-self.lookback_period:].max()
                
                # Deciding on allocation
                if current_price <= low_200 * self.buy_threshold:
                    allocation[ticker] = 1  # Full investment signal
                elif current_price >= high_200 * self.sell_threshold:
                    allocation[ticker] = 0  # Exit signal
                else:
                    # Maintain previous position; for simplicity, we treat it as neutral
                    # In a live setting, you'd check existing positions
                    allocation[ticker] = 0.5  # Neutral allocation
            else:
                # Not enough data, so we do nothing
                allocation[ticker] = 0

        return TargetAllocation(allocation)