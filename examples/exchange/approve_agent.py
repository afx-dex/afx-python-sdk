from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.approve_agent(
    agent_name="afx-python-sdk-example",
    validity_seconds=604800,
)
print(result)
