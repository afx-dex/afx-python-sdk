import os
import struct
import sys
import unittest
from pathlib import Path

from eth_account import Account
from eth_hash.auto import keccak

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class SigningTests(unittest.TestCase):
    def setUp(self):
        master = Account.create()
        agent = Account.create()
        os.environ["AFX_MASTER_PRIVATE_KEY"] = master.key.hex()
        os.environ["AFX_AGENT_PRIVATE_KEY"] = agent.key.hex()

    def test_connection_id_matches_afx_little_endian_spec(self):
        from afx import build_connection_id

        proto_bytes = b"\x08\x01\x12\x05hello"
        vault_address = "0x00000000000000000000000000000000000000ab"
        nonce = 1763023626904
        expiry_after = 1763023686

        expected = keccak(
            proto_bytes
            + bytes.fromhex(vault_address[2:])
            + struct.pack("<Q", nonce)
            + struct.pack("<Q", expiry_after)
        )

        self.assertEqual(
            build_connection_id(proto_bytes, vault_address, nonce, expiry_after),
            expected,
        )

    def test_agent_signature_has_padded_components(self):
        from afx import TESTNET
        from afx import Wallet
        from afx import sign_agent_payload

        signature = sign_agent_payload(
            Wallet.from_env(),
            TESTNET,
            proto_bytes=b"\x08\x01",
            nonce=1,
            expiry_after=None,
            vault_address=None,
        )

        self.assertRegex(signature["r"], r"^0x[0-9a-f]{64}$")
        self.assertRegex(signature["s"], r"^0x[0-9a-f]{64}$")
        self.assertIn(signature["v"], (27, 28))


if __name__ == "__main__":
    unittest.main()
