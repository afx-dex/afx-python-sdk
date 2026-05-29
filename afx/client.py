from afx.exchange import ExchangeClient
from afx.info import InfoClient
from afx.utils.config import get_environment
from afx.utils.http import HttpTransport
from afx.utils.wallet import AGENT_PRIVATE_KEY_ENV
from afx.utils.wallet import MASTER_PRIVATE_KEY_ENV
from afx.utils.wallet import Wallet
from afx.websocket import WebSocketClient


class AfxClient:
    def __init__(
        self,
        *,
        wallet,
        environment=None,
        testnet=True,
        transport=None,
        timeout=15,
    ):
        self.environment = environment or get_environment(testnet=testnet)
        self.wallet = wallet
        self.transport = transport or HttpTransport(
            self.environment.base_url,
            timeout=timeout,
        )
        self.info = InfoClient(
            self.transport,
            default_user_address=wallet.master_address,
        )
        self.exchange = ExchangeClient(self.transport, self.environment, wallet)
        self.websocket = WebSocketClient(
            self.environment.ws_url,
            default_user_address=wallet.master_address,
        )

    @classmethod
    def from_env(
        cls,
        testnet=True,
        transport=None,
        timeout=15,
        master_env=MASTER_PRIVATE_KEY_ENV,
        agent_env=AGENT_PRIVATE_KEY_ENV,
    ):
        return cls(
            wallet=Wallet.from_env(master_env=master_env, agent_env=agent_env),
            environment=get_environment(testnet=testnet),
            transport=transport,
            timeout=timeout,
        )
