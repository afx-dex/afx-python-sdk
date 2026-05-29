from dataclasses import dataclass


@dataclass(frozen=True)
class Environment:
    name: str
    base_url: str
    ws_url: str
    chain_id: int
    source: str
    dex_chain: str


MAINNET = Environment(
    name="mainnet",
    base_url="https://api.afx.xyz",
    ws_url="wss://ws.afx.xyz/ws/dex",
    chain_id=42161,
    source="a",
    dex_chain="Mainnet",
)

TESTNET = Environment(
    name="testnet",
    base_url="https://api-testnet.afx.xyz",
    ws_url="wss://ws-testnet.afx.xyz/ws/dex",
    chain_id=421614,
    source="b",
    dex_chain="Testnet",
)


def get_environment(testnet=True):
    return TESTNET if testnet else MAINNET
