#import backtrader as bt
import yfinance as yf
import datetime

class SMACross(bt.Strategy):
    params = dict(
        pfast=50,
        pslow=200,
        stake_pct=0.10,
    )

    def __init__(self):
        sma_fast = bt.ind.SMA(period=self.p.pfast)
        sma_slow = bt.ind.SMA(period=self.p.pslow)
        self.crossover = bt.ind.CrossOver(sma_fast, sma_slow)

    def next(self):
        cash = self.broker.get_cash()
        size = (cash * self.p.stake_pct) // self.data.close[0]

        if not self.position and self.crossover > 0:
            self.buy(size=size)

        elif self.position and self.crossover < 0:
            self.close()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SMACross)

    # Fetch historical BBAI data
    data = bt.feeds.PandasData(
        dataname=yf.download('BBAI', 
                             start='2022-01-01', 
                             end=datetime.date.today().isoformat())
    )
    cerebro.adddata(data)

    # Set capital and commission
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown,    _name='drawdown')

    # Run backtest
    results = cerebro.run()
    strat = results[0]

    # Print metrics
    print('Final Portfolio Value: $%.2f' % cerebro.broker.getvalue())
    print('Sharpe Ratio:', strat.analyzers.sharpe.get_analysis().get('sharperatio'))
    dd = strat.analyzers.drawdown.get_analysis()
    print('Max Drawdown: %.2f%%' % dd.max.drawdown)

    # Plot equity curve
    cerebro.plot(style='candlestick') code here