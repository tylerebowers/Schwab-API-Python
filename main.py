import asyncio
from utilities import client
from utilities import stream
from apis import quotes
from apis import priceHistory

client.login()
client.setupStream()
print(quotes.getQuote('AMD'))
print(priceHistory.getPriceHistory('AMD', 'day', '1', 'minute', '30', 'false'))
asyncio.run(stream.startStream())

