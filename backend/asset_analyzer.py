#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
from asset_data import AssetData

class AssetAnalyzer:
    def __init__(self, ticker, start_date, end_date, market_ticker="^GSPC"):
        self.asset_data = AssetData(ticker, start_date, end_date)
        self.market_data = AssetData(market_ticker, start_date, end_date)
        self.ticker = ticker
        self.market_ticker = market_ticker

    def sharpes_ratio(self):
        from empyrical import sharpe_ratio
        return sharpe_ratio(self.asset_data.daily_returns)

    def alpha_beta(self):
        from empyrical import alpha_beta
        return alpha_beta(
            self.asset_data.daily_returns, self.market_data.daily_returns
        )

    def max_drawdown(self):
        from empyrical import max_drawdown
        return max_drawdown(self.asset_data.daily_returns)

    def annual_return(self):
        from empyrical import annual_return
        return annual_return(self.asset_data.daily_returns)

    def annual_volatility(self):
        from empyrical import annual_volatility
        return annual_volatility(self.asset_data.daily_returns)

    def plot(self):
        from empyrical import cum_returns
        plt.figure()
        cum_returns(self.market_data.daily_returns).plot()
        cum_returns(self.asset_data.daily_returns).plot()
        plt.legend([f"{self.market_ticker} Returns", f"{self.ticker} Returns"])
        plt.title(f"{self.ticker} vs Market ({self.market_ticker})")
        plt.ylabel("Returns")
        plt.xlabel("Date")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze an asset.")
    parser.add_argument("ticker", help="Ticker symbol for the asset")
    parser.add_argument("start_date", help="Start date for data range (YYYY-MM-DD)")
    parser.add_argument("end_date", help="End date for data range (YYYY-MM-DD)")
    parser.add_argument(
        "--market_ticker",
        default="^GSPC",
        help="Market ticker symbol for beta calculation",
    )
    parser.add_argument(
        "--plot", action="store_true", help="Plot adjusted close prices"
    )

    args = parser.parse_args()
    analyzer = AssetAnalyzer(
        args.ticker, args.start_date, args.end_date, args.market_ticker
    )

    sharpe_ratio = analyzer.sharpes_ratio()
    alpha, beta = analyzer.alpha_beta()
    max_drawdown = analyzer.max_drawdown()
    annual_return = analyzer.annual_return()
    annual_volatility = analyzer.annual_volatility()

    print(f"Analyzing {args.ticker} from {args.start_date} to {args.end_date}...")
    print(f"Market ticker: {args.market_ticker}")
    print(f"Sharpe Ratio: {sharpe_ratio}")
    print(f"Alpha: {alpha}")
    print(f"Beta: {beta}")
    print(f"Annual Return: {annual_return}")
    print(f"Annual Volatility: {annual_volatility}")
    print(f"Max Drawdown: {max_drawdown}")

    if args.plot:
        analyzer.plot()
        plt.show()
