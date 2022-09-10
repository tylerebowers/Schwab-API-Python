import asyncio
from utilities import client
from utilities import stream
from apis import quotes
from apis import priceHistory

client.login()
client.setupStream()
print(quotes.getQuote('AMD'))
#Steaming will be updated to make usage more logical in the near future (hint: threading)
asyncio.run(stream.startStream())

