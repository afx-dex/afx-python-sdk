import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


EXPECTED_EXAMPLES = {
    "examples/info/get_products.py",
    "examples/info/get_wallet.py",
    "examples/info/get_orders.py",
    "examples/info/get_positions.py",
    "examples/info/get_kline.py",
    "examples/info/get_funding_rate_current.py",
    "examples/info/get_agents.py",
    "examples/info/get_active_agent.py",
    "examples/exchange/faucet_claim.py",
    "examples/exchange/approve_agent.py",
    "examples/exchange/revoke_agent.py",
    "examples/exchange/withdraw.py",
    "examples/exchange/place_order.py",
    "examples/exchange/place_tp_sl_orders.py",
    "examples/exchange/cancel_order.py",
    "examples/exchange/cancel_all.py",
    "examples/exchange/set_leverage.py",
    "examples/exchange/set_margin_mode.py",
    "examples/exchange/assign_pos_margin.py",
    "examples/exchange/bind_referral.py",
    "examples/exchange/vault_deposit.py",
    "examples/exchange/vault_withdraw.py",
    "examples/websocket/subscribe.py",
    "examples/websocket/subscribe_order_book.py",
    "examples/websocket/subscribe_ticker.py",
    "examples/websocket/subscribe_account_state.py",
    "examples/advanced/multiple_wallets.py",
}


class ExampleTests(unittest.TestCase):
    def test_every_public_feature_has_an_example(self):
        missing = [
            path
            for path in sorted(EXPECTED_EXAMPLES)
            if not (ROOT / path).exists()
        ]

        self.assertEqual(missing, [])

    def test_examples_do_not_accept_or_print_private_keys(self):
        unsafe_tokens = [
            "master_key=",
            "agent_key=",
            "private_key=",
            "YOUR_MASTER_PRIVATE_KEY",
            "YOUR_AGENT_PRIVATE_KEY",
            "print(os.environ",
        ]

        for path in sorted((ROOT / "examples").glob("**/*.py")):
            text = path.read_text()
            for token in unsafe_tokens:
                self.assertNotIn(token, text, str(path))


if __name__ == "__main__":
    unittest.main()
