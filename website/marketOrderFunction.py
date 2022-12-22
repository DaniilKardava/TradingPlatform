import time
import json
import cbpro

c = cbpro.PublicClient()


def marketOrder(requestArguments, request, Wallet, db):
    # Check if bought or sold:
    if "buyButton" in requestArguments:
        transactionSide = "Buy"
    else:
        transactionSide = "Sell"

    # Get asset name
    assetTransacted = request.form.get("assetTransacted")

    # Get price first fast
    data = c.get_product_ticker(
        product_id=assetTransacted+"-USD")
    currentPrice = float(data["price"])

    print(currentPrice)

    transactionTime = int(time.time())

    # Get quantity
    quantityTransacted = float(request.form.get("QTY"))

    # Get user address
    userAddress = request.form.get("userAddress")

    # Find user in database
    user = Wallet.query.filter_by(wallet_address=userAddress).first()

    # Get and change existing holdings
    assetAmounts = json.loads(user.asset_amounts)

    if transactionSide == "Buy":
        if assetTransacted not in list(assetAmounts.keys()):
            # Deduct cash, this is pure purchase of an asset
            user.cash_amount -= currentPrice * quantityTransacted
            # add quantity and average fill price
            assetAmounts[assetTransacted] = [
                quantityTransacted, quantityTransacted * currentPrice]
        elif (assetAmounts[assetTransacted][0] == 0):
            # Deduct cash, this is pure purchase of an asset
            user.cash_amount -= currentPrice * quantityTransacted
            # add quantity and average fill price
            assetAmounts[assetTransacted] = [
                quantityTransacted, assetAmounts[assetTransacted][1] + quantityTransacted * currentPrice]
        else:
            preTransactionShares = assetAmounts[assetTransacted][0]
            preTransactionAvgCost = assetAmounts[assetTransacted][1] / \
                preTransactionShares

            # If the asset exists as a short position and the transaction cross 0
            if (preTransactionShares < 0 and (abs(preTransactionShares) < quantityTransacted)):
                # Add back short position value: (2 * entry) - current
                user.cash_amount += (
                    2 * preTransactionAvgCost - currentPrice) * abs(preTransactionShares)

                user.cash_amount -= currentPrice * \
                    (quantityTransacted - abs(preTransactionShares))

                assetAmounts[assetTransacted] = [
                    preTransactionShares + quantityTransacted, assetAmounts[assetTransacted][1] + quantityTransacted * currentPrice]

            elif (preTransactionShares < 0 and (abs(preTransactionShares) >= quantityTransacted)):
                # If asset exists as short position but the buy back isnt large enough to turn positive
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
            # Deduct cash, the asset is being sold short with borrowed funds, 1:1 collateral
            user.cash_amount -= currentPrice * quantityTransacted
            assetAmounts[assetTransacted] = [-1 *
                                             quantityTransacted, -1 *
                                             quantityTransacted * currentPrice]

        elif assetAmounts[assetTransacted][0] == 0:
            # Deduct cash, the asset is being sold short with borrowed funds, 1:1 collateral
            user.cash_amount -= currentPrice * quantityTransacted
            assetAmounts[assetTransacted] = [-1 *
                                             quantityTransacted, assetAmounts[assetTransacted][1] - quantityTransacted * currentPrice]

        else:
            preTransactionShares = assetAmounts[assetTransacted][0]
            preTransactionAvgCost = assetAmounts[assetTransacted][1] / \
                preTransactionShares

            # If position is positive but sells across 0
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

            elif (preTransactionShares < 0):
                user.cash_amount -= quantityTransacted * currentPrice

                assetAmounts[assetTransacted] = [
                    preTransactionShares - quantityTransacted, assetAmounts[assetTransacted][1] - quantityTransacted * currentPrice]

    user.asset_amounts = json.dumps(assetAmounts)

    # Add to transaction history, same form as trade log
    transactionHistory = json.loads(user.transaction_history)

    transactionHistory.append(
        [transactionTime, transactionSide, assetTransacted, quantityTransacted, currentPrice])

    user.transaction_history = json.dumps(transactionHistory)

    db.session.commit()

    for column in Wallet.__table__.columns:
        column = column.name
        print(getattr(user, column))
