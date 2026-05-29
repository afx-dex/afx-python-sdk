from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.info.get_funding_rate_current(symbol="BTCUSDC")
print(result)
