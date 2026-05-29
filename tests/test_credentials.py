import inspect
import os
import subprocess
import sys
import unittest
from pathlib import Path

from eth_account import Account

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class WalletTests(unittest.TestCase):
    def setUp(self):
        for name in [
            "AFX_MASTER_PRIVATE_KEY",
            "AFX_AGENT_PRIVATE_KEY",
            "AFX_BOT1_MASTER_PRIVATE_KEY",
            "AFX_BOT1_AGENT_PRIVATE_KEY",
            "AFX_BOT2_MASTER_PRIVATE_KEY",
            "AFX_BOT2_AGENT_PRIVATE_KEY",
        ]:
            os.environ.pop(name, None)

    def test_wallet_is_loaded_from_env_only(self):
        from afx import Wallet

        with self.assertRaisesRegex(EnvironmentError, "AFX_MASTER_PRIVATE_KEY"):
            Wallet.from_env()

        master = Account.create()
        agent = Account.create()
        os.environ["AFX_MASTER_PRIVATE_KEY"] = master.key.hex()
        os.environ["AFX_AGENT_PRIVATE_KEY"] = agent.key.hex()

        wallet = Wallet.from_env()

        self.assertEqual(wallet.master_address, master.address)
        self.assertEqual(wallet.agent_address, agent.address)

    def test_wallet_supports_multiple_env_account_agent_pairs(self):
        from afx import Wallet

        master_one = Account.create()
        agent_one = Account.create()
        master_two = Account.create()
        agent_two = Account.create()
        os.environ["AFX_BOT1_MASTER_PRIVATE_KEY"] = master_one.key.hex()
        os.environ["AFX_BOT1_AGENT_PRIVATE_KEY"] = agent_one.key.hex()
        os.environ["AFX_BOT2_MASTER_PRIVATE_KEY"] = master_two.key.hex()
        os.environ["AFX_BOT2_AGENT_PRIVATE_KEY"] = agent_two.key.hex()

        wallet_one = Wallet.from_env(
            master_env="AFX_BOT1_MASTER_PRIVATE_KEY",
            agent_env="AFX_BOT1_AGENT_PRIVATE_KEY",
        )
        wallet_two = Wallet.from_env(
            master_env="AFX_BOT2_MASTER_PRIVATE_KEY",
            agent_env="AFX_BOT2_AGENT_PRIVATE_KEY",
        )

        self.assertEqual(wallet_one.master_address, master_one.address)
        self.assertEqual(wallet_one.agent_address, agent_one.address)
        self.assertEqual(wallet_two.master_address, master_two.address)
        self.assertEqual(wallet_two.agent_address, agent_two.address)

    def test_wallet_repr_does_not_leak_private_keys(self):
        from afx import Wallet

        master = Account.create()
        agent = Account.create()
        os.environ["AFX_MASTER_PRIVATE_KEY"] = master.key.hex()
        os.environ["AFX_AGENT_PRIVATE_KEY"] = agent.key.hex()

        wallet = Wallet.from_env()
        rendered = repr(wallet)

        self.assertIn("Wallet(", rendered)
        self.assertIn(master.address, rendered)
        self.assertIn(agent.address, rendered)
        self.assertNotIn(master.key.hex(), rendered)
        self.assertNotIn(agent.key.hex(), rendered)

    def test_public_api_uses_wallet_not_credentials(self):
        import afx

        self.assertFalse(hasattr(afx, "Credentials"))

    def test_client_exposes_wallet_as_primary_name(self):
        from afx import AfxClient

        master = Account.create()
        agent = Account.create()
        os.environ["AFX_MASTER_PRIVATE_KEY"] = master.key.hex()
        os.environ["AFX_AGENT_PRIVATE_KEY"] = agent.key.hex()

        client = AfxClient.from_env(testnet=True)

        self.assertEqual(client.wallet.master_address, master.address)
        self.assertFalse(hasattr(client, "credentials"))

    def test_client_accepts_explicit_wallets_for_multiple_accounts(self):
        from afx import AfxClient
        from afx import Wallet

        class FakeTransport:
            def __init__(self):
                self.get_calls = []

            def get(self, path, params=None):
                self.get_calls.append((path, params or {}))
                return {"code": 0, "data": []}

        first_master = Account.create()
        first_agent = Account.create()
        second_master = Account.create()
        second_agent = Account.create()
        first_transport = FakeTransport()
        second_transport = FakeTransport()

        first_client = AfxClient(
            wallet=Wallet(first_master, first_agent),
            testnet=True,
            transport=first_transport,
        )
        second_client = AfxClient(
            wallet=Wallet(second_master, second_agent),
            testnet=True,
            transport=second_transport,
        )

        first_client.info.get_wallet()
        second_client.info.get_wallet()

        self.assertEqual(
            first_transport.get_calls[-1],
            ("/info/account/wallet", {"userAddr": first_master.address}),
        )
        self.assertEqual(
            second_transport.get_calls[-1],
            ("/info/account/wallet", {"userAddr": second_master.address}),
        )

    def test_client_from_env_accepts_custom_env_names(self):
        from afx import AfxClient

        class FakeTransport:
            def __init__(self):
                self.get_calls = []

            def get(self, path, params=None):
                self.get_calls.append((path, params or {}))
                return {"code": 0, "data": []}

        master = Account.create()
        agent = Account.create()
        os.environ["AFX_BOT1_MASTER_PRIVATE_KEY"] = master.key.hex()
        os.environ["AFX_BOT1_AGENT_PRIVATE_KEY"] = agent.key.hex()
        transport = FakeTransport()

        client = AfxClient.from_env(
            testnet=True,
            transport=transport,
            master_env="AFX_BOT1_MASTER_PRIVATE_KEY",
            agent_env="AFX_BOT1_AGENT_PRIVATE_KEY",
        )
        client.info.get_wallet()

        self.assertEqual(client.wallet.master_address, master.address)
        self.assertEqual(client.wallet.agent_address, agent.address)
        self.assertEqual(
            transport.get_calls[-1],
            ("/info/account/wallet", {"userAddr": master.address}),
        )

    def test_public_client_api_has_no_private_key_parameters(self):
        from afx import AfxClient
        from afx import Wallet

        public_signatures = [
            inspect.signature(AfxClient),
            inspect.signature(AfxClient.from_env),
            inspect.signature(Wallet),
            inspect.signature(Wallet.from_env),
        ]
        for signature in public_signatures:
            self.assertNotIn("master_key", signature.parameters)
            self.assertNotIn("agent_key", signature.parameters)
            self.assertNotIn("private_key", signature.parameters)

    def test_package_imports_work_after_directory_move(self):
        from afx import HttpTransport
        from afx.protos import dex_pb2
        from afx.utils.http import HttpTransport as DirectHttpTransport

        self.assertIs(HttpTransport, DirectHttpTransport)
        self.assertTrue(hasattr(dex_pb2, "MsgPlaceOrders"))

    def test_afx_subpackages_do_not_shadow_stdlib_types(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "afx")

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import types; print(types.ModuleType.__name__)",
            ],
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "module")


if __name__ == "__main__":
    unittest.main()
