from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.set_margin_mode(symbol_code=1, mode="CROSS")
print(result)
