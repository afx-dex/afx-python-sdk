from afx import AfxClient


client = AfxClient.from_env(testnet=True)
result = client.exchange.place_order(
    symbol_code=1,
    px="50000",
    qty="0.001",
    side="BUY",
    ord_type="LIMIT",
    tif="GTC",
)
print(result)
