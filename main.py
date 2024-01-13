from flask import Flask, request, render_template, send_from_directory, jsonify
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path += "/backend/"
sys.path.append(dir_path)
from portfolio_optimizer import PortfolioOptimizer
from asset_analyzer import AssetAnalyzer
import matplotlib.pyplot as plt
import io
import urllib
import base64
import numpy as np

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/portfolio", methods=["GET"])
def portfolio():
    return render_template("portfolio_analysis.html")


@app.route("/patents", methods=["GET"])
def patents():
    return render_template("patents.html")


def process_portfolio(data, optimize):
    tickers = data.getlist("tickers[]")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    analyzer = PortfolioOptimizer(tickers, start_date, end_date)
    weights = []
    if optimize:
        weights = analyzer.optimize_portfolio_sharpe()
    else:
        weights = data.getlist("weights[]")
        weights = [float(weight) for weight in weights]
        # normalize weights so they're all equal to 1
        total_weights = np.sum(weights)
        weights = [weight / total_weights for weight in weights]

    portfolio_return = round(analyzer.annual_return(weights) * 100, 1)
    portfolio_volatility = round(analyzer.annual_volatility(weights) * 100, 1)
    sharpe_ratio = round(analyzer.sharpe_ratio(weights), 2)
    alpha, beta = analyzer.alpha_beta(weights)
    alpha = round(alpha, 2)
    beta = round(beta, 2)
    max_drawdown = round(analyzer.max_drawdown(weights) * 100, 1)
    plt.figure()
    analyzer.plot(weights)
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = urllib.parse.quote(base64.b64encode(img.read()).decode())

    if optimize:
        # express weights as a percentage
        weights = [str(round(weight * 100)) + "%" for weight in weights]

    return render_template(
        "results.html",
        portfolio_results={
            "return": f"{portfolio_return} %",
            "volatility": f"{portfolio_volatility} %",
            "sharpe_ratio": sharpe_ratio,
            "alpha": alpha,
            "beta": beta,
            "max_drawdown": f"{max_drawdown} %",
            "optimized": optimize,
            "optimized_weights": dict(zip(tickers, weights)),
        },
        plot_url=plot_url,
    )


@app.route("/optimize_portfolio", methods=["POST"])
def optimize_portfolio():
    data = request.form
    return process_portfolio(data, True)


@app.route("/analyze_portfolio", methods=["POST"])
def analyze_portfolio():
    data = request.form
    return process_portfolio(data, False)


@app.route("/analyze_asset", methods=["POST"])
def analyze_asset():
    data = request.form
    ticker = data.get("ticker")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    analyzer = AssetAnalyzer(ticker, start_date, end_date)
    # Call the methods of the AssetAnalyzer class and get the results
    # For example:
    asset_return = round(analyzer.annual_return() * 100, 1)
    asset_volatility = round(analyzer.annual_volatility() * 100, 1)
    sharpe_ratio = round(analyzer.sharpes_ratio(), 2)
    alpha, beta = analyzer.alpha_beta()
    alpha = round(alpha, 2)
    beta = round(beta, 2)
    max_drawdown = round(analyzer.max_drawdown() * 100, 1)
    analyzer.plot()
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = urllib.parse.quote(base64.b64encode(img.read()).decode())

    return render_template(
        "results.html",
        asset_results={
            "asset": ticker,
            "asset_return": f"{asset_return} %",
            "asset_volatility": f"{asset_volatility} %",
            "sharpe_ratio": sharpe_ratio,
            "alpha": alpha,
            "beta": beta,
            "max_drawdown": f"{max_drawdown} %",
        },
        plot_url=plot_url,
    )


@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(os.path.join("static", "images"), filename)


if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='192.168.100.253', debug=True, port=5000) # for running on local network (use ifconfig to get your IP address)
