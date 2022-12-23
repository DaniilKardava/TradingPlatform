import time
import json
# coinbase pro data api 
import cbpro

# Instance of public client class, used to make requests to coinbase
c = cbpro.PublicClient()

# Function to update user's portfolio status after a transaction. 
# Accepts 4 arguments. The request contains key:value pairs. The request arguments is a list of the keys, one of which should either be a sell or buy button.
# Also accepts Wallet, the sql database class that defines how user data is stored. Finally, accepts db, an instance of the sql database used in the flask app. 

def marketOrder(requestArguments, request, Wallet, db):
    
    # Check if bought or sold:
    if "buyButton" in requestArguments:
        transactionSide = "Buy"
    else:
        transactionSide = "Sell"

    # Get asset name, references the assetTransaced key to get its value. 
    assetTransacted = request.form.get("assetTransacted")

    # Get price of asset
    data = c.get_product_ticker(
        product_id=assetTransacted+"-USD")
    currentPrice = float(data["price"])

    print(currentPrice)

    transactionTime = int(time.time())

    # Get quantity transacted by user
    quantityTransacted = float(request.form.get("QTY"))

    # Get user blockchain address
    userAddress = request.form.get("userAddress")

    # Find user in database
    user = Wallet.query.filter_by(wallet_address=userAddress).first()

    # Get existing user holdings
    assetAmounts = json.loads(user.asset_amounts)

    # This takes care of logical scenarios for either buy or sell: a) User shrinks their position but not enough to change direction from Long to Short or vice verse, 
    # b) User reverses their position, Long to Short or vice verse c) User simply increases their position, more Short or more Long.
    # In each case, I want to change my cash balance, and update my dictionary containing asset balances for a user, including the amount, and the total dollar value.
    if transactionSide == "Buy":
        if assetTransacted not in list(assetAmounts.keys()):
            # If user has never made a transaction with this asset.
            # Deduct cash, this is pure purchase of an asset
            user.cash_amount -= currentPrice * quantityTransacted
            # add quantity and average fill price
            assetAmounts[assetTransacted] = [
                quantityTransacted, quantityTransacted * currentPrice]
        elif (assetAmounts[assetTransacted][0] == 0):
            # If user has previously transacted with this asset and it exists as a key in the dictionary, but currently has no position open. 
            # Deduct cash, this is pure purchase of an asset
            user.cash_amount -= currentPrice * quantityTransacted
            # add quantity and average fill price
            assetAmounts[assetTransacted] = [
                quantityTransacted, assetAmounts[assetTransacted][1] + quantityTransacted * currentPrice]
        else:
            preTransactionShares = assetAmounts[assetTransacted][0]
            preTransactionAvgCost = assetAmounts[assetTransacted][1] / \
                preTransactionShares

            # If the asset exists as a short position and the transaction crosses 0 -> becomes long position
            if (preTransactionShares < 0 and (abs(preTransactionShares) < quantityTransacted)):
                # Add back short position value that is being closed: (2 * entry price) - current price... ex: short at 100 -> price now 95 -> 
                # 2 * 100 - 95 = 105, reflects 5$ profit.
                user.cash_amount += (
                    2 * preTransactionAvgCost - currentPrice) * abs(preTransactionShares)
                
                # Deduct dollar value of shares that now make up long position.
                user.cash_amount -= currentPrice * \
                    (quantityTransacted - abs(preTransactionShares))

                assetAmounts[assetTransacted] = [
                    preTransactionShares + quantityTransacted, assetAmounts[assetTransacted][1] + quantityTransacted * currentPrice]

            elif (preTransactionShares < 0 and (abs(preTransactionShares) >= quantityTransacted)):
                
                # If asset exists as short position but the buy back isnt large enough to turn shares owned positive
                user.cash_amount += (
                    2 * preTransactionAvgCost - currentPrice) * quantityTransacted

                assetAmounts[assetTransacted] = [
                    preTransactionShares + quantityTransacted, assetAmounts[assetTransacted][1] + quantityTransacted * currentPrice]

            elif (preTransactionShares > 0):
                # If the position was already positive
                user.cash_amount -= currentPrice * quantityTransacted

                assetAmounts[assetTransacted] = [
                    preTransactionShares + quantityTransacted, assetAmounts[assetTransacted][1] + quantityTransacted * currentPrice]
    else:
        if assetTransacted not in list(assetAmounts.keys()):
            # Deduct cash, the asset is being sold short with "borrowed" funds, 1:1 collateral
            user.cash_amount -= currentPrice * quantityTransacted
            assetAmounts[assetTransacted] = [-1 *
                                             quantityTransacted, -1 *
                                             quantityTransacted * currentPrice]

        elif assetAmounts[assetTransacted][0] == 0:
            user.cash_amount -= currentPrice * quantityTransacted
            assetAmounts[assetTransacted] = [-1 *
                                             quantityTransacted, assetAmounts[assetTransacted][1] - quantityTransacted * currentPrice]

        else:
            preTransactionShares = assetAmounts[assetTransacted][0]
            preTransactionAvgCost = assetAmounts[assetTransacted][1] / \
                preTransactionShares

            # If position is positive but sells across 0 -> becomes short position
            if (preTransactionShares > 0 and (preTransactionShares < quantityTransacted)):
                user.cash_amount += preTransactionShares * currentPrice
                user.cash_amount -= (quantityTransacted -
                                     preTransactionShares) * currentPrice

                assetAmounts[assetTransacted] = [
                    preTransactionShares - quantityTransacted, assetAmounts[assetTransacted][1] - quantityTransacted * currentPrice]

            # If position is positive but doesnt sell across 0
            elif (preTransactionShares > 0 and (preTransactionShares >= quantityTransacted)):
                user.cash_amount += quantityTransacted * currentPrice

                assetAmounts[assetTransacted] = [
                    preTransactionShares - quantityTransacted, assetAmounts[assetTransacted][1] - quantityTransacted * currentPrice]
            
            # If position was already short
            elif (preTransactionShares < 0):
                user.cash_amount -= quantityTransacted * currentPrice

                assetAmounts[assetTransacted] = [
                    preTransactionShares - quantityTransacted, assetAmounts[assetTransacted][1] - quantityTransacted * currentPrice]
                
    # Update database values
    user.asset_amounts = json.dumps(assetAmounts)

    # Get existing trade history
    transactionHistory = json.loads(user.transaction_history)
    
    # Update history
    transactionHistory.append(
        [transactionTime, transactionSide, assetTransacted, quantityTransacted, currentPrice])

    user.transaction_history = json.dumps(transactionHistory)

    db.session.commit()
    
    # Print updated values
    for column in Wallet.__table__.columns:
        column = column.name
        print(getattr(user, column))
