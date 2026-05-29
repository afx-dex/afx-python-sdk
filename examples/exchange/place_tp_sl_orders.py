from afx import AfxClient


client = AfxClient.from_env(testnet=True)

take_profit = client.exchange.place_order(
    symbol_code=1,
    px="0",
    qty="0",
    side="SELL",
    ord_type="MARKET",
    tif="IOC",
    reduce_only_option="TP_FROM_POSITION",
    trigger_px="90000",
    trigger_type="LAST_PRICE",
    slippage_pct="0.001",
)
print(take_profit)

stop_loss = client.exchange.place_order(
    symbol_code=1,
    px="0",
    qty="0",
    side="SELL",
    ord_type="MARKET",
    tif="IOC",
    reduce_only_option="SL_FROM_POSITION",
    trigger_px="70000",
    trigger_type="LAST_PRICE",
    slippage_pct="0.001",
)
print(stop_loss)
