# AFX Python SDK

Python SDK for AFX DEX. The SDK is split into separate clients for read-only info queries, signed exchange actions, and WebSocket subscriptions.

## Install Dependencies

```bash
python3 -m pip install eth-account eth-hash protobuf requests websockets
```

For local development from this repository:

```bash
export PYTHONPATH=.
```

## Wallet

Private keys are loaded only from environment variables:

- `AFX_MASTER_PRIVATE_KEY`
- `AFX_AGENT_PRIVATE_KEY`

Set them through your shell, deployment secret manager, or CI secret store. Do not paste them into source files or examples, and do not print these values. The SDK does not accept private keys through public client constructors.

`Wallet` is the SDK object for signing, following the common Python DEX SDK style of passing wallet/account objects around internally.

For multiple account/agent pairs in one process, load each pair from distinct environment variables and pass the wallet explicitly:

```python
from afx import AfxClient, Wallet

primary_wallet = Wallet.from_env(
    master_env="AFX_PRIMARY_MASTER_PRIVATE_KEY",
    agent_env="AFX_PRIMARY_AGENT_PRIVATE_KEY",
)
hedge_wallet = Wallet.from_env(
    master_env="AFX_HEDGE_MASTER_PRIVATE_KEY",
    agent_env="AFX_HEDGE_AGENT_PRIVATE_KEY",
)

primary = AfxClient(wallet=primary_wallet, testnet=True)
hedge = AfxClient(wallet=hedge_wallet, testnet=True)
```

## Quick Start

```python
from afx import AfxClient

client = AfxClient.from_env(testnet=True)
products = client.info.get_products()
print(products)
```

Trading actions are under `client.exchange`, read-only queries are under `client.info`, and WebSocket helpers are under `client.websocket`.

Agent-signed actions serialize with the vendored generated protobuf module `afx.protos.dex_pb2`, produced from the AFX DEX protobuf definitions. The SDK does not hand-roll protobuf wire encoding.

`expiryAfter` is sent and signed as a millisecond timestamp. `validitySeconds` remains a duration in seconds, so one hour is `3600`.

For market orders, `slippage_pct` is a decimal ratio string such as `"0.001"`. TP/SL orders use the Python parameter `reduce_only_option`, for example `"TP_FROM_POSITION"` or `"SL_FROM_POSITION"`; the SDK keeps the generated protobuf field correct and converts the action payload to the server field used by each exchange action.

`ord_type` request values should be active order types such as `"LIMIT"` or `"MARKET"`. The generated protobuf enum also contains the default `"NONE"` value and display-only values used by query/stream responses: `"MARKET_LIQ_SELLOFF"`, `"LIMIT_LIQ_SELLOFF"`, `"ADL"`, and `"LIQUIDATION"`. Do not pass those values to order request methods.

## Examples

Every public SDK feature has an example under `examples/`:

```bash
PYTHONPATH=. python3 examples/info/get_products.py
PYTHONPATH=. python3 examples/exchange/place_order.py
PYTHONPATH=. python3 examples/exchange/replace_order.py
PYTHONPATH=. python3 examples/exchange/place_bracket_order.py
PYTHONPATH=. python3 examples/websocket/subscribe_ticker.py
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```
