from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.cancel_all(symbol_code=1)
print(result)
