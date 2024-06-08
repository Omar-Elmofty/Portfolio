#!/usr/bin/env python3

import numpy as np
from asset_data import AssetData
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import empyrical


class PortfolioOptimizer:
    def __init__(
        self,
        tickers,
        start_date,
        end_date,
        market_ticker="^GSPC",
        sharpe_weight=1.0,
        return_weight=0.0,
        volatility_weight=0.0,
    ):
        self.assets = [AssetData(ticker, start_date, end_date) for ticker in tickers]
        self.market_data = AssetData(market_ticker, start_date, end_date)
        self.data = self.combine_data()
        self.data_pct_change = self.data.pct_change()
        self.data_pct_change.dropna(inplace=True)

        # Store weights
        self.sharpe_weight = sharpe_weight
        self.return_weight = return_weight
        self.volatility_weight = volatility_weight

        # Calculate the baseline performance of market
        self.market_sharpe_ratio = empyrical.sharpe_ratio(
            self.market_data.daily_returns.values
        )
        self.market_annual_return = empyrical.annual_return(
            self.market_data.daily_returns.values
        )
        self.market_annual_volatility = empyrical.annual_volatility(
            self.market_data.daily_returns.values
        )

    def combine_data(self):
        data = pd.concat([asset.data["Adj Close"] for asset in self.assets], axis=1)
        data.columns = [asset.ticker for asset in self.assets]
        return data

    def portfolio_returns(self, weights):
        # maintain the index of the data
        weights_df = pd.DataFrame(weights, index=self.data.columns)
        return self.data_pct_change.mul(weights_df[0], axis=1).sum(axis=1)

    def sharpe_ratio(self, weights):
        return empyrical.sharpe_ratio(self.portfolio_returns(weights))

    def alpha_beta(self, weights):
        return empyrical.alpha_beta(
            self.portfolio_returns(weights), self.market_data.daily_returns
        )

    def max_drawdown(self, weights):
        return empyrical.max_drawdown(self.portfolio_returns(weights))

    def annual_return(self, weights):
        return empyrical.annual_return(self.portfolio_returns(weights))

    def annual_volatility(self, weights):
        return empyrical.annual_volatility(self.portfolio_returns(weights))

    def optimize_portfolio(self):
        num_assets = len(self.assets)
        args = ()
        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        bound = (0.0, 1.0)
        bounds = tuple(bound for asset in range(num_assets))
        result = minimize(
            self.cost,
            num_assets
            * [
                1.0 / num_assets,
            ],
            args=args,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        if not result.success:
            raise BaseException(result.message)
        return result.x

    def optimize_portfolio_sharpe(self):
        self.sharpe_weight = 1
        self.return_weight = 0
        self.volatility_weight = 0
        return self.optimize_portfolio()

    def optimize_portfolio_return(self):
        self.sharpe_weight = 0
        self.return_weight = 1
        self.volatility_weight = 0
        return self.optimize_portfolio()

    def cost(self, weights):
        return (
            -self.sharpe_weight * self.sharpe_ratio(weights) / self.market_sharpe_ratio
            - self.return_weight
            * self.annual_return(weights)
            / self.market_annual_return
            + self.volatility_weight
            * self.annual_volatility(weights)
            / self.market_annual_volatility
        )

    def plot(self, weights):
        # Calculate the portfolio value as the dot product of the weights and the asset prices
        portfolio_returns = self.portfolio_returns(weights)
        portfolio_returns_df = pd.DataFrame(portfolio_returns, index=self.data.index)
        plt.plot(empyrical.cum_returns(self.market_data.daily_returns))
        plt.plot(empyrical.cum_returns(portfolio_returns_df))
        plt.legend([f"Market {self.market_data.ticker} returns", f"Portfolio Returns"])
        plt.title(f"Portfolio vs Market ({self.market_data.ticker})")
        plt.xlabel("Time")
        plt.ylabel("Returns")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize a portfolio of assets.")
    parser.add_argument(
        "-t", "--tickers", nargs="+", required=True, help="List of asset tickers."
    )
    parser.add_argument(
        "-s", "--start_date", required=True, help="Start date in YYYY-MM-DD format."
    )
    parser.add_argument(
        "-e", "--end_date", required=True, help="End date in YYYY-MM-DD format."
    )
    parser.add_argument(
        "--market_ticker",
        default="^GSPC",
        help="Market ticker symbol for beta calculation",
    )
    parser.add_argument(
        "--sharpe_weight",
        type=float,
        default=1.0,
        help="Sharpe ratio weight for optimization",
    )
    parser.add_argument(
        "--return_weight",
        type=float,
        default=0.0,
        help="Return weight for optimization",
    )
    parser.add_argument(
        "--volatility_weight",
        type=float,
        default=0.0,
        help="Volatility weight for optimization",
    )
    parser.add_argument(
        "--weights",
        nargs="+",
        type=float,
        default=None,
        help="List of weights for the assets, if not provided, the optimizer will calculate the optimal weights",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot the portfolio value over time",
    )
    parser.add_argument(
        "--print_market_returns",
        action="store_true",
        help="Print the market returns",
    )
    args = parser.parse_args()

    optimizer = PortfolioOptimizer(
        args.tickers,
        args.start_date,
        args.end_date,
        args.market_ticker,
        args.sharpe_weight,
        args.return_weight,
        args.volatility_weight,
    )
    weights = args.weights
    if weights is None:
        weights = optimizer.optimize_portfolio()

    if len(weights) != len(args.tickers):
        raise BaseException(
            f"Number of weights {len(weights)} does not match number of assets {len(optimizer.assets)}"
        )

    if not np.isclose(np.sum(weights), 1.0):
        raise BaseException(
            f"Weights must sum to 1.0, but sum of weights is {np.sum(weights)}"
        )

    sharpe_ratio = optimizer.sharpe_ratio(weights)
    alpha, beta = optimizer.alpha_beta(weights)
    max_drawdown_value = optimizer.max_drawdown(weights)
    variance = optimizer.annual_volatility(weights)

    print(f"The assets are: {[asset.ticker for asset in optimizer.assets]}")
    # print rounded weights in 2 decimal places
    print(f"The optimal weights are: {[round(weight,2) for weight in weights]}")
    print(f"The portfolio annual return is: {optimizer.annual_return(weights)}")
    print(f"The portfolio annual volatility is: {variance}")
    print(f"The portfolio Sharpe ratio is: {sharpe_ratio}")
    print(f"The portfolio alpha is: {alpha}")
    print(f"The portfolio beta is: {beta}")
    print(f"The portfolio maximum drawdown is: {max_drawdown_value}")

    if args.print_market_returns:
        print("Market returns:")
        print(f"The market annual return is: {optimizer.market_annual_return}")
        print(f"The market annual volatility is: {optimizer.market_annual_volatility}")
        print(f"The market Sharpe ratio is: {optimizer.market_sharpe_ratio}")

    if args.plot:
        optimizer.plot(weights)
        plt.show()
