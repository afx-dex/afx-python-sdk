from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.faucet_claim()
print(result)
