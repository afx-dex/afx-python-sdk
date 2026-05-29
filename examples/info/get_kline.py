from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.info.get_kline(symbol_name="BTCUSDC", interval="60", limit=10)
print(result)
