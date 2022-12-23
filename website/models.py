from . import db
from sqlalchemy import Text

# Define a model to store user info
class Wallet(db.Model):
    # Blockchain wallet address set as primary key
    wallet_address = db.Column(db.String, primary_key=True)
    cash_amount = db.Column(db.Integer)
    
    # {"BTC":[amount,dollar value],...}
    asset_amounts = db.Column(Text)
    
    # [[date, side, asset, amount, price],...]
    transaction_history = db.Column(Text)
    
    # [{"date":...,"value":...},...] , to graph performance of user, updated daily.
    portfolio_history = db.Column(Text)
    
    # Timestamp of first wallet connection to site
    date_created = db.Column(db.Integer)
