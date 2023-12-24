#!/usr/bin/env python3

import yfinance as yf
import os
import pandas as pd


class AssetData:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.download_data(self.ticker)
        self.daily_returns = self.calculate_daily_returns()

    def download_data(self, ticker):
        directory = "market_data"
        filename = f"{directory}/{ticker}_{self.start_date}_{self.end_date}.csv"
        if not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.exists(filename):
            # Load data from CSV file if it exists
            data = pd.read_csv(filename, index_col="Date")
            # Convert the 'Date' column to datetime format
            data.index = pd.to_datetime(data.index)
        else:
            # Download historical data as a dataframe
            data = yf.download(ticker, start=self.start_date, end=self.end_date)
            # Save data to CSV file
            data.to_csv(filename)
        data["daily_returns"] = data["Adj Close"].pct_change()
        data.dropna(inplace=True)
        return data

    def calculate_daily_returns(self):
        daily_returns = self.data["Adj Close"].pct_change()
        daily_returns.dropna(inplace=True)
        return daily_returns
