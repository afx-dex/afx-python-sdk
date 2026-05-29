from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.info.get_agents(status="ACTIVE", page=1, page_size=20)
print(result)
