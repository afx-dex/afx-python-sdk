from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.set_leverage(symbol_code=1, leverage="10")
print(result)
