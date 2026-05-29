# AFX Python SDK Design

## Goal

Build a small, secure Python SDK for AFX DEX that follows the AFX docs in `../afx-docs` and borrows Hyperliquid-style separation between read-only info, signed exchange actions, and WebSocket subscriptions.

## Scope

The first SDK version covers the quickstart path and common workflows:

- Environment-only credentials.
- EIP-712 signing for master and agent operations.
- REST transport for Info and Exchange APIs.
- WebSocket subscription helpers.
- Examples for every public feature in the first version.
- Unit tests for credentials, signing, request shape, examples, and API ergonomics.

## Security

Private keys are never accepted as public constructor arguments. Users must put keys in `AFX_MASTER_PRIVATE_KEY` and `AFX_AGENT_PRIVATE_KEY`, then call `AfxClient.from_env()`.

Credential objects hide private material in `repr`, do not expose key accessors, and examples never print or log private keys. Tests scan examples and public constructor signatures to prevent regressions.

## Architecture

`src/afx/config.py` defines environments. `src/afx/credentials.py` loads accounts from env. `src/afx/signing.py` owns EIP-712 signing and connection id logic. `src/afx/protobuf.py` owns protobuf wire serialization for signed agent messages. `src/afx/http.py` owns REST calls. `src/afx/info.py`, `src/afx/exchange.py`, and `src/afx/websocket.py` expose separate API groups. `src/afx/client.py` is a light convenience facade.

## API Shape

Users can start with:

```python
from afx import AfxClient

client = AfxClient.from_env(testnet=True)
client.info.get_products()
client.exchange.place_order(symbol_code=1, px="50000", qty="0.001")
```

The SDK returns decoded JSON dictionaries without printing responses. Callers decide what to log.

## Examples

Examples live under `examples/info`, `examples/exchange`, and `examples/websocket`. Each public SDK feature has a corresponding example file. Examples read credentials only from environment variables.

## Verification

Local verification uses `python3 -m unittest discover -s tests -v`. End-to-end testnet verification generates ephemeral wallets inside the process, stores them in env, claims faucet funds, approves the agent, queries products/wallet state, and opens a WebSocket subscription without printing private keys.
