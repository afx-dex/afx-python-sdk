import time

from afx import AfxClient


client = AfxClient.from_env(testnet=True)
cl_ord_id = int(time.time() * 1000)

place_result = client.exchange.place_order(
    symbol_code=1,
    px="50000",
    qty="0.001",
    side="BUY",
    ord_type="LIMIT",
    tif="GTC",
    cl_ord_id=cl_ord_id,
)
print(place_result)

replace_result = client.exchange.replace_order(
    symbol_code=1,
    px="50100",
    qty="0.001",
    side="BUY",
    ord_type="LIMIT",
    tif="GTC",
    cl_ord_id=cl_ord_id,
)
print(replace_result)
