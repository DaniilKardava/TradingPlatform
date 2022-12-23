from flask import Blueprint, render_template, request
from .models import Wallet
from . import db
from .marketOrderFunction import marketOrder

# Defines a blueprint, a way to organize endpoints
views = Blueprint("views", __name__, )


# Below are endpoints that a user can reach, and the function that is to be executed when that happens.
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

    if request.method == "POST":
        # Get list of keys from the key:value pairs that come with the request. Use them to check the origin of the request.
        requestArguments = list(request.form)

        # Check if the post request matches the format that comes from the html form that is connected to chart timeframe buttons.
        if requestArguments[0] in ["1mTimeFrame", "5mTimeFrame", "15mTimeFrame", "1hTimeFrame", "6hTimeFrame", "1dTimeFrame"]:
            timeframe = requestArguments[0]

        if "assetSearchRequest" in requestArguments:
            assetName = requestArguments[1]

        # Buy / Sell market order request
        if "QTY" in requestArguments:
            marketOrder(requestArguments, request, Wallet, db)
            
    # Variables can be passed to the html to display cutom values.
    return render_template("tradeStation.html", assetName=assetName, assetList=assetList, timeframe=timeframe)


# End point to check if user already exists.
@ views.route('/check-user')
def check_user():
    wallet_address = request.args.get('wallet_address')
    user = Wallet.query.filter_by(wallet_address=wallet_address).first()
    if user:
        return {'exists': True}
    else:
        return {'exists': False}

# End point to add a user. 
@ views.route('/add-user')
def add_user():

    wallet_address = request.args.get('wallet_address')
    cashAmount = request.args.get('cashAmount')
    assetsOwned = request.args.get('assetsOwned')
    transactionsMade = request.args.get('transactionsMade')
    portfolioHistory = request.args.get('portfolioHistory')
    dateCreated = request.args.get('dateCreated')

    user = Wallet(wallet_address=wallet_address, cash_amount=cashAmount, asset_amounts=assetsOwned,
                  transaction_history=transactionsMade, portfolio_history=portfolioHistory, date_created=dateCreated)

    db.session.add(user)

    try:
        db.session.commit()
        return {'success': True}
    except:
        return {'success': False}

# End point to get user info and display it on the page.
@ views.route('/get-user-info')
def get_user_info():
    walletAddress = request.args.get("wallet_address")
    user = Wallet.query.filter_by(wallet_address=walletAddress).first()
    return {"cash": user.cash_amount, "assetsOwned": user.asset_amounts, "tradeLog": user.transaction_history, "accountPerformance": user.portfolio_history}
