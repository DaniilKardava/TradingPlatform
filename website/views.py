from flask import Blueprint, render_template, request
from .models import Wallet
from . import db
from .marketOrderFunction import marketOrder

views = Blueprint("views", __name__, )

# When we go to the / route from our homepage, we will run the following code


@views.route("/", methods=["POST", "GET"])
def home():
    return render_template("onboarding.html")


@views.route("/leaderboard", methods=["POST", "GET"])
def leaderboard():
    return render_template("leaderboard.html")


assetList = ["BTC", "ETH", "DOGE"]
assetName = "BTC"
timeframe = "1dTimeFrame"


@views.route("/tradeStation", methods=["POST", "GET"])
def tradeStation():
    global assetList
    global assetName
    global timeframe
    # First time initialization

    if request.method == "POST":
        requestArguments = list(request.form)

        # Check if the post request is for the chart timeframe
        if requestArguments[0] in ["1mTimeFrame", "5mTimeFrame", "15mTimeFrame", "1hTimeFrame", "6hTimeFrame", "1dTimeFrame"]:
            timeframe = requestArguments[0]
            print(timeframe)

        # Checking source of post request and how to appropriately handle
        if "assetSearchRequest" in requestArguments:
            assetName = requestArguments[1]

        # Buy / Sell market request
        if "QTY" in requestArguments:
            marketOrder(requestArguments, request, Wallet, db)

    return render_template("tradeStation.html", assetName=assetName, assetList=assetList, timeframe=timeframe)


@ views.route('/check-user')
def check_user():
    wallet_address = request.args.get('wallet_address')
    user = Wallet.query.filter_by(wallet_address=wallet_address).first()
    if user:
        return {'exists': True}
    else:
        return {'exists': False}


@ views.route('/add-user')
def add_user():

    wallet_address = request.args.get('wallet_address')
    cashAmount = request.args.get('cashAmount')
    assetsOwned = (request.args.get('assetsOwned'))
    transactionsMade = (request.args.get('transactionsMade'))
    portfolioHistory = (request.args.get('portfolioHistory'))
    dateCreated = request.args.get('dateCreated')

    print(portfolioHistory)
    user = Wallet(wallet_address=wallet_address, cash_amount=cashAmount, asset_amounts=assetsOwned,
                  transaction_history=transactionsMade, portfolio_history=portfolioHistory, date_created=dateCreated)

    db.session.add(user)

    try:
        db.session.commit()
        return {'success': True}
    except:
        return {'success': False}


@ views.route('/get-user-info')
def get_user_info():
    walletAddress = request.args.get("wallet_address")
    user = Wallet.query.filter_by(wallet_address=walletAddress).first()
    return {"cash": user.cash_amount, "assetsOwned": user.asset_amounts, "tradeLog": user.transaction_history, "accountPerformance": user.portfolio_history}
