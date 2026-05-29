from afx import AfxClient
from afx import Wallet


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

print(primary.info.get_wallet())
print(hedge.info.get_wallet())
