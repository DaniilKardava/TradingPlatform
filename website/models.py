from . import db
from sqlalchemy import Text


class Wallet(db.Model):
    wallet_address = db.Column(db.String, primary_key=True)
    # Below are dictionaries storing asset:[amount,totalEarnings] and transaction history with same format as tradelog and time:portfolioValue
    cash_amount = db.Column(db.Integer)
    asset_amounts = db.Column(Text)
    transaction_history = db.Column(Text)
    portfolio_history = db.Column(Text)
    # Timestamp
    date_created = db.Column(db.Integer)
