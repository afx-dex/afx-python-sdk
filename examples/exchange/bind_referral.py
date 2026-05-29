from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.bind_referral(code="AFX")
print(result)
