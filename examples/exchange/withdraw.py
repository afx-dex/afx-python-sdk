from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.withdraw(
    destination="0x0000000000000000000000000000000000000000",
    amount="1",
)
print(result)
