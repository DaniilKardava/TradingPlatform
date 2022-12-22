from datetime import datetime, timezone, timedelta
import cbpro
from prettytable import PrettyTable
import requests
import math
import time

c = cbpro.PublicClient()


# Set up a requests session and a hook to intercept the HTTP request
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=3)
session.mount('https://', adapter)


def hook(response, *args, **kwargs):
    print(response.url)


session.hooks['response'] = [hook]

# Set the session for the Coinbase Pro client
c.session = session


while True:
    data = c.get_product_ticker("BTC-USD")
    print(data)
    time.sleep(.2)


# Send a request to the Coinbase Pro API
currentDate = datetime.now(timezone.utc) + timedelta(minutes=1)
startDate = currentDate - timedelta(days=10)
# startDate = startDate.isoformat()

endDate = math.floor(currentDate.timestamp())

startDate = endDate - (300 * 60)


gran = 60

for a in range(10):
    data = c.get_product_historic_rates(
        product_id='BTC-USD', granularity=gran, start=startDate, end=endDate)
    endDate = startDate
    startDate = endDate - (300 * 60)
    table = PrettyTable()
    table.field_names = ["Date", "Low", "High", "Open", "Close", "Volume"]

    for row in data:
        date = datetime.fromtimestamp(row[0])
        table.add_row([date, row[1], row[2], row[3], row[4], row[5]])

    # Print the table
    print(table)


'''
currentDate = datetime.now(timezone.utc) + timedelta(days=1)
startDate = currentDate - timedelta(days=100)
currentDate = currentDate.isoformat()

data = (c.get_product_historic_rates(product_id='BTC-USD',
                                     granularity=86400, start=startDate, ))

table = PrettyTable()
table.field_names = ["Date", "Low", "High", "Open", "Close", "Volume"]

for row in data:
    date = datetime.fromtimestamp(row[0])
    table.add_row([date, row[1], row[2], row[3], row[4], row[5]])

# Print the table
print(table)
'''
