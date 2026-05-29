# AFX Python SDK Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify a secure AFX Python SDK with standard implementation modules and examples for every public feature.

**Architecture:** Implement a `src/afx` package with separate credentials, signing, protobuf, transport, info, exchange, websocket, and facade modules. Use environment-only key loading and focused unit tests to enforce security and request correctness.

**Tech Stack:** Python 3.9+, `eth-account`, `eth-hash`, `requests`, `websockets`, `unittest`.

---

### Task 1: Test Security And API Shape

**Files:**
- Create: `tests/test_credentials.py`
- Create: `tests/test_signing.py`
- Create: `tests/test_clients.py`
- Create: `tests/test_examples.py`

- [ ] Write failing tests that assert env-only credentials, hidden repr, signer output shape, request body shape, and example safety.
- [ ] Run `python3 -m unittest discover -s tests -v` and confirm imports fail because SDK modules do not exist yet.

### Task 2: Implement Core SDK Modules

**Files:**
- Create: `src/afx/__init__.py`
- Create: `src/afx/config.py`
- Create: `src/afx/credentials.py`
- Create: `src/afx/signing.py`
- Create: `src/afx/protobuf.py`
- Create: `src/afx/http.py`
- Create: `src/afx/info.py`
- Create: `src/afx/exchange.py`
- Create: `src/afx/websocket.py`
- Create: `src/afx/client.py`
- Create: `pyproject.toml`

- [ ] Implement the smallest SDK that passes the unit tests.
- [ ] Keep signing, protobuf, REST, query, exchange, and websocket code in separate files.
- [ ] Run `python3 -m unittest discover -s tests -v`.

### Task 3: Add Examples

**Files:**
- Create one example per public feature under `examples/info`, `examples/exchange`, and `examples/websocket`.

- [ ] Add examples that use `AfxClient.from_env(testnet=True)`.
- [ ] Do not include private key literals or constructor key arguments.
- [ ] Run example safety tests.

### Task 4: End-To-End Testnet Smoke

**Files:**
- Create: `tests/e2e_testnet_smoke.py`

- [ ] Generate ephemeral master and agent wallets inside the script.
- [ ] Store generated private keys in env only.
- [ ] Run faucet claim, approve agent, product query, wallet query, and one WebSocket subscription.
- [ ] Print only addresses and response status summaries, never private keys.

### Task 5: Final Verification

- [ ] Run `python3 -m unittest discover -s tests -v`.
- [ ] Run a package import check from the repository root.
- [ ] Run the testnet smoke script if network access is available.
- [ ] Review public API names, examples, and security constraints for friendliness and safety.
