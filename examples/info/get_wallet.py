from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.info.get_wallet()
print(result)
