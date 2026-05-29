from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.vault_withdraw(
    vault_address="0x0000000000000000000000000000000000000000",
    amount="1",
    currency_code=1,
)
print(result)
