from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.cancel_order(symbol_code=1, ord_id="12345")
print(result)
