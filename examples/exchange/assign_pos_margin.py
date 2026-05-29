from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.assign_pos_margin(symbol_code=1, amount="10")
print(result)
