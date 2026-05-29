import os

from eth_account import Account


MASTER_PRIVATE_KEY_ENV = "AFX_MASTER_PRIVATE_KEY"
AGENT_PRIVATE_KEY_ENV = "AFX_AGENT_PRIVATE_KEY"


class Wallet:
    """Environment-backed signing wallet.

    Private keys are intentionally stored only in private attributes and are
    never included in repr output.
    """

    def __init__(self, master_account, agent_account):
        self._master_account = master_account
        self._agent_account = agent_account

    @classmethod
    def from_env(
        cls,
        *,
        master_env=MASTER_PRIVATE_KEY_ENV,
        agent_env=AGENT_PRIVATE_KEY_ENV,
    ):
        master_key = os.environ.get(master_env)
        if not master_key:
            raise EnvironmentError(f"{master_env} is required")

        agent_key = os.environ.get(agent_env)
        if not agent_key:
            raise EnvironmentError(f"{agent_env} is required")

        return cls(
            master_account=Account.from_key(master_key),
            agent_account=Account.from_key(agent_key),
        )

    @property
    def master_address(self):
        return self._master_account.address

    @property
    def agent_address(self):
        return self._agent_account.address

    def sign_with_master(self, full_message):
        return Account.sign_typed_data(
            private_key=self._master_account.key,
            full_message=full_message,
        )

    def sign_with_agent(self, full_message):
        return Account.sign_typed_data(
            private_key=self._agent_account.key,
            full_message=full_message,
        )

    def __repr__(self):
        return (
            "Wallet("
            f"master_address={self.master_address!r}, "
            f"agent_address={self.agent_address!r})"
        )
