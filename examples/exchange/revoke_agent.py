from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.revoke_agent(agent_name="app.afx.xyz")
print(result)
