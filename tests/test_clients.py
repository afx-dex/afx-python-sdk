import inspect
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from eth_account import Account

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class FakeTransport:
    def __init__(self):
        self.get_calls = []
        self.post_calls = []

    def get(self, path, params=None):
        self.get_calls.append((path, params or {}))
        return {"code": 0, "data": {"path": path, "params": params or {}}}

    def post(self, path, body):
        self.post_calls.append((path, body))
        return {"code": 0, "data": {"path": path, "body": body}}


class FakeHttpResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        raise AssertionError("JSON API errors should be returned, not raised")


class FakeSession:
    def __init__(self, response):
        self.response = response

    def post(self, *args, **kwargs):
        return self.response


class ClientTests(unittest.TestCase):
    def setUp(self):
        master = Account.create()
        agent = Account.create()
        os.environ["AFX_MASTER_PRIVATE_KEY"] = master.key.hex()
        os.environ["AFX_AGENT_PRIVATE_KEY"] = agent.key.hex()
        self.master_address = master.address
        self.agent_address = agent.address
        self.transport = FakeTransport()

    def test_info_client_uses_read_only_info_paths(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        response = client.info.get_wallet()

        self.assertEqual(response["code"], 0)
        self.assertEqual(
            self.transport.get_calls[-1],
            ("/info/account/wallet", {"userAddr": self.master_address}),
        )

    def test_info_client_queries_agent_list_and_active_agent(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        client.info.get_agents(status="ACTIVE", page=1, page_size=100)
        self.assertEqual(
            self.transport.get_calls[-1],
            (
                "/info/account/agent",
                {
                    "userAddr": self.master_address,
                    "status": "ACTIVE",
                    "page": 1,
                    "pageSize": 100,
                },
            ),
        )

        client.info.get_active_agent(agent_name="unit-agent")
        self.assertEqual(
            self.transport.get_calls[-1],
            (
                "/info/account/agent/active",
                {"userAddr": self.master_address, "agentName": "unit-agent"},
            ),
        )

    def test_place_order_builds_signed_exchange_request(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        client.exchange.place_order(
            symbol_code=1,
            px="50000",
            qty="0.001",
            side="BUY",
            ord_type="LIMIT",
            tif="GTC",
            nonce=123,
        )

        path, body = self.transport.post_calls[-1]
        self.assertEqual(path, "/api/v1/exchange")
        self.assertEqual(body["nonce"], 123)
        self.assertEqual(body["action"]["type"], "placeOrder")
        self.assertEqual(body["action"]["orders"][0]["symbolCode"], 1)
        self.assertEqual(body["action"]["orders"][0]["ordSide"], "BUY")
        self.assertIn("signature", body)
        self.assertNotIn("vaultAddress", body)

    def test_conditional_order_uses_server_reduce_only_action_key(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        client.exchange.place_order(
            symbol_code=1,
            px="0",
            qty="0",
            side="SELL",
            ord_type="MARKET",
            tif="IOC",
            reduce_only_option="TP_FROM_POSITION",
            trigger_px="90000",
            trigger_type="LAST_PRICE",
            slippage_pct="0.001",
            nonce=124,
        )

        _, body = self.transport.post_calls[-1]
        order = body["action"]["orders"][0]
        self.assertEqual(order["reduceOnlyOption"], "TP_FROM_POSITION")
        self.assertNotIn("reduce_only_option", order)

    def test_replace_order_builds_signed_exchange_request(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        client.exchange.replace_order(
            symbol_code=1,
            px="50100",
            qty="0.002",
            side="SELL",
            ord_type="LIMIT",
            tif="GTC",
            ord_id=88,
            cl_ord_id=77,
            nonce=125,
        )

        path, body = self.transport.post_calls[-1]
        self.assertEqual(path, "/api/v1/exchange")
        self.assertEqual(body["nonce"], 125)
        self.assertEqual(
            body["action"],
            {
                "type": "replaceOrder",
                "symbolCode": 1,
                "ordPx": "50100",
                "ordQty": "0.002",
                "ordType": "LIMIT",
                "ordSide": "SELL",
                "timeInForce": "GTC",
                "ordId": 88,
                "clOrdId": 77,
            },
        )
        self.assertIn("signature", body)

    def test_replace_order_requires_existing_order_identifier(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)

        with self.assertRaises(ValueError):
            client.exchange.replace_order(
                symbol_code=1,
                px="50100",
                qty="0.002",
                side="SELL",
                ord_type="LIMIT",
                tif="GTC",
            )

    def test_place_bracket_order_builds_signed_exchange_request(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        client.exchange.place_bracket_order(
            main_order={
                "symbol_code": 1,
                "px": "50000",
                "qty": "0.001",
                "side": "BUY",
                "ord_type": "LIMIT",
                "tif": "GTC",
                "cl_ord_id": 11,
            },
            take_profit_order={
                "symbol_code": 1,
                "px": "55000",
                "qty": "0.001",
                "trigger_px": "55000",
                "side": "SELL",
                "ord_type": "LIMIT",
                "tif": "GTC",
                "reduce_only_option": "TP_FROM_POSITION",
                "trigger_type": "LAST_PRICE",
                "cl_ord_id": 12,
            },
            stop_loss_order={
                "symbol_code": 1,
                "px": "0",
                "qty": "0.001",
                "trigger_px": "45000",
                "side": "SELL",
                "ord_type": "MARKET",
                "tif": "IOC",
                "reduce_only_option": "SL_FROM_POSITION",
                "trigger_type": "LAST_PRICE",
                "slippage_pct": "0.01",
                "cl_ord_id": 13,
            },
            nonce=126,
        )

        path, body = self.transport.post_calls[-1]
        self.assertEqual(path, "/api/v1/exchange")
        self.assertEqual(body["nonce"], 126)
        self.assertEqual(body["action"]["type"], "placeBracketOrder")
        self.assertEqual(len(body["action"]["orders"]), 3)
        self.assertEqual(body["action"]["orders"][0]["clOrdId"], 11)
        self.assertEqual(body["action"]["orders"][1]["reduceOnly"], "TP_FROM_POSITION")
        self.assertEqual(body["action"]["orders"][2]["reduceOnly"], "SL_FROM_POSITION")
        self.assertNotIn("reduceOnlyOption", body["action"]["orders"][1])
        self.assertIn("signature", body)

    def test_master_signed_request_uses_same_outer_nonce_and_expiry(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        client.exchange.approve_agent(
            agent_name="unit-test",
            validity_seconds=604800,
            nonce=456,
            expiry_after=789,
        )

        _, body = self.transport.post_calls[-1]
        self.assertEqual(body["nonce"], 456)
        self.assertEqual(body["expiryAfter"], 789)
        self.assertEqual(body["action"]["agentAddress"], self.agent_address)
        self.assertEqual(body["action"]["dexChain"], "Testnet")

    def test_approve_agent_builds_expected_action(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        client.exchange.approve_agent(
            agent_name="unit-agent",
            validity_seconds=3600,
            nonce=111,
            expiry_after=222,
        )

        path, body = self.transport.post_calls[-1]
        self.assertEqual(path, "/api/v1/exchange")
        self.assertEqual(body["nonce"], 111)
        self.assertEqual(body["expiryAfter"], 222)
        self.assertEqual(
            body["action"],
            {
                "type": "approveAgent",
                "agentAddress": self.agent_address,
                "agentName": "unit-agent",
                "validitySeconds": 3600,
                "dexChain": "Testnet",
            },
        )
        self.assertIn("signature", body)

    def test_withdraw_includes_withdraw_sequence_in_action_and_eip712(self):
        from afx import AfxClient

        captured = {}

        def fake_sign_master_payload(wallet, environment, primary_type, type_fields, message):
            captured["primary_type"] = primary_type
            captured["type_fields"] = type_fields
            captured["message"] = message
            return {"r": "0x1", "s": "0x2", "v": 27}

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        with patch("afx.exchange.sign_master_payload", fake_sign_master_payload):
            client.exchange.withdraw(
                destination="0x0000000000000000000000000000000000000001",
                amount="3.5",
                withdraw_sequence=789,
                nonce=123,
                expiry_after=456,
            )

        _, body = self.transport.post_calls[-1]
        self.assertEqual(body["action"]["withdrawSequence"], 789)
        self.assertEqual(captured["primary_type"], "Withdraw")
        self.assertIn(
            {"name": "withdrawSequence", "type": "uint64"},
            captured["type_fields"],
        )
        self.assertEqual(captured["message"]["withdrawSequence"], 789)
        self.assertEqual(captured["message"]["nonce"], 123)

    def test_approve_agent_has_no_referral_code_parameter(self):
        from afx import ExchangeClient

        signature = inspect.signature(ExchangeClient.approve_agent)

        self.assertNotIn("referral_code", signature.parameters)

    def test_approve_agent_can_override_agent_address_for_revoke(self):
        from afx import AfxClient
        from afx.exchange import ZERO_ADDRESS

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        client.exchange.approve_agent(
            agent_name="unit-test",
            agent_address=ZERO_ADDRESS,
            validity_seconds=0,
            nonce=457,
            expiry_after=790,
        )

        _, body = self.transport.post_calls[-1]
        self.assertEqual(body["action"]["type"], "approveAgent")
        self.assertEqual(body["action"]["agentName"], "unit-test")
        self.assertEqual(body["action"]["agentAddress"], ZERO_ADDRESS)
        self.assertEqual(body["action"]["validitySeconds"], 0)

    def test_revoke_agent_uses_zero_agent_address(self):
        from afx import AfxClient
        from afx.exchange import ZERO_ADDRESS

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        client.exchange.revoke_agent(
            agent_name="unit-test",
            nonce=458,
            expiry_after=791,
        )

        _, body = self.transport.post_calls[-1]
        self.assertEqual(body["action"]["type"], "approveAgent")
        self.assertEqual(body["action"]["agentName"], "unit-test")
        self.assertEqual(body["action"]["agentAddress"], ZERO_ADDRESS)

    def test_expiry_seconds_are_converted_to_milliseconds(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        with patch("afx.exchange.time.time", return_value=1_700_000_000.123):
            client.exchange.approve_agent(expiry_seconds=3600)

        _, body = self.transport.post_calls[-1]
        self.assertEqual(body["nonce"], 1_700_000_000_123)
        self.assertEqual(body["expiryAfter"], 1_700_003_600_123)

    def test_generated_nonces_are_monotonic_within_a_client(self):
        from afx import AfxClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)
        with patch("afx.exchange.time.time", return_value=1_700_000_000.123):
            first = client.exchange._nonce(None)
            second = client.exchange._nonce(None)
            third = client.exchange._nonce(None)

        self.assertEqual(
            [first, second, third],
            [1_700_000_000_123, 1_700_000_000_124, 1_700_000_000_125],
        )

    def test_facade_exposes_separate_api_groups(self):
        from afx import AfxClient
        from afx import ExchangeClient
        from afx import InfoClient
        from afx import WebSocketClient

        client = AfxClient.from_env(testnet=True, transport=self.transport)

        self.assertIsInstance(client.info, InfoClient)
        self.assertIsInstance(client.exchange, ExchangeClient)
        self.assertIsInstance(client.websocket, WebSocketClient)

    def test_http_transport_returns_afx_json_error_payloads(self):
        from afx import HttpTransport

        response = FakeHttpResponse(
            400,
            {"code": 40231, "message": "Transaction broadcast failed", "data": None},
        )
        transport = HttpTransport(
            "https://api10-testnet.afx.xyz",
            session=FakeSession(response),
        )

        self.assertEqual(
            transport.post("/api/v1/exchange", {"action": {"type": "approveAgent"}}),
            {
                "code": 40231,
                "message": "Transaction broadcast failed",
                "data": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
