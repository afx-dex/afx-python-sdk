import time

from afx import AfxClient


client = AfxClient.from_env(testnet=True)
base_cl_ord_id = int(time.time() * 1000)

result = client.exchange.place_bracket_order(
    main_order={
        "symbol_code": 1,
        "px": "50000",
        "qty": "0.001",
        "side": "BUY",
        "ord_type": "LIMIT",
        "tif": "GTC",
        "cl_ord_id": base_cl_ord_id,
    },
    take_profit_order={
        "symbol_code": 1,
        "px": "55000",
        "qty": "0.001",
        "trigger_px": "55000",
        "side": "SELL",
        "ord_type": "LIMIT",
        "tif": "GTC",
        "reduce_only_option": "TP_FROM_POSITION",
        "trigger_type": "LAST_PRICE",
        "cl_ord_id": base_cl_ord_id + 1,
    },
    stop_loss_order={
        "symbol_code": 1,
        "px": "0",
        "qty": "0.001",
        "trigger_px": "45000",
        "side": "SELL",
        "ord_type": "MARKET",
        "tif": "IOC",
        "reduce_only_option": "SL_FROM_POSITION",
        "trigger_type": "LAST_PRICE",
        "slippage_pct": "0.01",
        "cl_ord_id": base_cl_ord_id + 2,
    },
)
print(result)
