from flask import Flask, request, render_template, send_from_directory, jsonify
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path += "/backend/"
sys.path.append(dir_path)

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path += "/factory_simulator/simulation_backend/"
sys.path.append(dir_path)

app = Flask(__name__)

@app.route("/get-lailabdy-token", methods=["GET"])
def get_token():

    # Lazy import to reduce ram usage
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request

    # Load the credentials from the service account key file
    credentials = service_account.Credentials.from_service_account_file(
        "./laila27bdy-firebase-adminsdk-8dsrx-a273543c63.json"
    )
    scoped_credentials = credentials.with_scopes(
        ["https://www.googleapis.com/auth/firebase.messaging"]
    )

    # Obtain an access token
    request = Request()
    scoped_credentials.refresh(request)

    # Return the access token.
    return jsonify({"access_token": scoped_credentials.token})


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
    # Lazy import to reduce ram usage
    from portfolio_optimizer import PortfolioOptimizer
    from numpy import sum as np_sum
    from base64 import b64encode
    from urllib import parse
    from io import BytesIO
    import matplotlib.pyplot as plt

    tickers = data.getlist("tickers[]")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    analyzer = PortfolioOptimizer(tickers, start_date, end_date)
    success, failed_ticker = analyzer.validate()
    if not (success):
        return jsonify({"error": f"No data found for {failed_ticker}"})

    weights = []
    if optimize:
        weights = analyzer.optimize_portfolio_sharpe()
    else:
        weights = data.getlist("weights[]")
        weights = [float(weight) for weight in weights]
        # normalize weights so they're all equal to 1
        total_weights = np_sum(weights)
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
    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = parse.quote(b64encode(img.read()).decode())

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
    from asset_analyzer import AssetAnalyzer
    from base64 import b64encode
    from urllib import parse
    from io import BytesIO
    import matplotlib.pyplot as plt

    data = request.form
    ticker = data.get("ticker")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    analyzer = AssetAnalyzer(ticker, start_date, end_date)
    success, failed_ticker = analyzer.validate()
    if not (success):
        return jsonify({"error": f"No data found for {failed_ticker}"})
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
    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = parse.quote(b64encode(img.read()).decode())

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


@app.route("/personal_projects", methods=["GET"])
def personal_projects():
    return render_template("personal_projects.html")


@app.route("/factory_simulator", methods=["GET"])
def index():
    return render_template("factory_simulator.html")


@app.route("/knowledge_compendium/", methods=["GET"])
def knowledge_compendium():
    try:
        return send_from_directory("knowledge_compendium/knowledge_compendium/_build/html/", "index.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/knowledge_compendium/<path:filename>", methods=["GET"])
def get_template_file(filename):
    try:
        return send_from_directory("knowledge_compendium/knowledge_compendium/_build/html/", filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/simulate", methods=["POST"])
def simulate():
    if request.method == "POST":
        stats_dict = {}
        try:
            import model
            import json
            request_json = request.get_json()
            model_json = json.loads(request_json["model"])
            model = model.createModelFromGoJSJson(model_json)
            simulation_time = int(request_json["simulation_time"])
            model.run(simulation_time)
            stats_dict = model.statistics()
        except Exception as e:
            import traceback2 as traceback
            print(e)
            traceback.print_exc()
            stats_dict = {"error": str(e), "traceback": traceback.format_exc()}
        return {"output": stats_dict}


if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='192.168.100.253', debug=True, port=5000) # for running on local network (use ifconfig to get your IP address)
