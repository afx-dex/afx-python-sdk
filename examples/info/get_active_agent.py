from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.info.get_active_agent(agent_name="app.afx.xyz")
print(result)
