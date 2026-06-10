import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ProtobufTests(unittest.TestCase):
    def test_place_orders_serialization_uses_generated_dex_pb2(self):
        from afx.utils import protobuf
        from afx.protos import dex_pb2

        expected = dex_pb2.MsgPlaceOrders(
            orders=[
                dex_pb2.MsgPlaceOrder(
                    symbol_code=1,
                    ord_px="50000",
                    ord_qty="0.001",
                    ord_type=dex_pb2.LIMIT,
                    ord_side=dex_pb2.BUY,
                    time_in_force=dex_pb2.GTC,
                )
            ]
        ).SerializeToString()

        actual = protobuf.place_orders(
            [
                {
                    "symbol_code": 1,
                    "px": "50000",
                    "qty": "0.001",
                    "ord_type": "LIMIT",
                    "side": "BUY",
                    "tif": "GTC",
                }
            ]
        )

        self.assertEqual(actual, expected)

    def test_replace_order_serialization_uses_generated_dex_pb2(self):
        from afx.utils import protobuf
        from afx.protos import dex_pb2

        expected = dex_pb2.MsgReplaceOrder(
            cl_ord_id=77,
            symbol_code=1,
            ord_px="50100",
            ord_qty="0.002",
            ord_type=dex_pb2.LIMIT,
            ord_side=dex_pb2.SELL,
            time_in_force=dex_pb2.GTC,
            ord_id=88,
        ).SerializeToString()

        actual = protobuf.replace_order(
            {
                "symbol_code": 1,
                "px": "50100",
                "qty": "0.002",
                "ord_type": "LIMIT",
                "side": "SELL",
                "tif": "GTC",
                "cl_ord_id": 77,
                "ord_id": 88,
            }
        )

        self.assertEqual(actual, expected)

    def test_place_bracket_order_serialization_uses_generated_dex_pb2(self):
        from afx.utils import protobuf
        from afx.protos import dex_pb2

        main_order = dex_pb2.MsgPlaceOrder(
            cl_ord_id=11,
            symbol_code=1,
            ord_px="50000",
            ord_qty="0.001",
            ord_type=dex_pb2.LIMIT,
            ord_side=dex_pb2.BUY,
            time_in_force=dex_pb2.GTC,
        )
        take_profit_order = dex_pb2.MsgPlaceOrder(
            cl_ord_id=12,
            symbol_code=1,
            ord_px="55000",
            ord_qty="0.001",
            trigger_px="55000",
            ord_type=dex_pb2.LIMIT,
            ord_side=dex_pb2.SELL,
            time_in_force=dex_pb2.GTC,
            reduce_only_option=dex_pb2.TP_FROM_POSITION,
            tpsl_trigger_type=dex_pb2.LAST_PRICE,
        )
        stop_loss_order = dex_pb2.MsgPlaceOrder(
            cl_ord_id=13,
            symbol_code=1,
            ord_px="0",
            ord_qty="0.001",
            trigger_px="45000",
            ord_type=dex_pb2.MARKET,
            ord_side=dex_pb2.SELL,
            time_in_force=dex_pb2.IOC,
            reduce_only_option=dex_pb2.SL_FROM_POSITION,
            tpsl_trigger_type=dex_pb2.LAST_PRICE,
            slippage_pct="0.01",
        )
        expected = dex_pb2.MsgPlaceBracketOrder(
            main_order=main_order,
            take_profit_order=take_profit_order,
            stop_loss_order=stop_loss_order,
        ).SerializeToString()

        actual = protobuf.place_bracket_order(
            [
                {
                    "symbol_code": 1,
                    "px": "50000",
                    "qty": "0.001",
                    "ord_type": "LIMIT",
                    "side": "BUY",
                    "tif": "GTC",
                    "cl_ord_id": 11,
                },
                {
                    "symbol_code": 1,
                    "px": "55000",
                    "qty": "0.001",
                    "trigger_px": "55000",
                    "ord_type": "LIMIT",
                    "side": "SELL",
                    "tif": "GTC",
                    "reduce_only_option": "TP_FROM_POSITION",
                    "trigger_type": "LAST_PRICE",
                    "cl_ord_id": 12,
                },
                {
                    "symbol_code": 1,
                    "px": "0",
                    "qty": "0.001",
                    "trigger_px": "45000",
                    "ord_type": "MARKET",
                    "side": "SELL",
                    "tif": "IOC",
                    "reduce_only_option": "SL_FROM_POSITION",
                    "trigger_type": "LAST_PRICE",
                    "slippage_pct": "0.01",
                    "cl_ord_id": 13,
                },
            ]
        )

        self.assertEqual(actual, expected)

    def test_display_only_order_types_cannot_be_used_in_requests(self):
        from afx.utils import protobuf
        from afx.protos import dex_pb2

        for ord_type in (
            "MARKET_LIQ_SELLOFF",
            "LIMIT_LIQ_SELLOFF",
            "ADL",
            "LIQUIDATION",
            dex_pb2.MARKET_LIQ_SELLOFF,
            dex_pb2.LIMIT_LIQ_SELLOFF,
            dex_pb2.ADL,
            dex_pb2.LIQUIDATION,
        ):
            with self.subTest(ord_type=ord_type):
                with self.assertRaisesRegex(ValueError, "display-only"):
                    protobuf.place_orders(
                        [
                            {
                                "symbol_code": 1,
                                "px": "50000",
                                "qty": "0.001",
                                "ord_type": ord_type,
                                "side": "BUY",
                                "tif": "GTC",
                            }
                        ]
                    )

    def test_none_order_type_cannot_be_used_in_requests(self):
        from afx.utils import protobuf
        from afx.protos import dex_pb2

        for ord_type in ("NONE", dex_pb2.ORD_TYPE_NONE):
            with self.subTest(ord_type=ord_type):
                with self.assertRaisesRegex(ValueError, "ord_type must be one of"):
                    protobuf.place_orders(
                        [
                            {
                                "symbol_code": 1,
                                "px": "50000",
                                "qty": "0.001",
                                "ord_type": ord_type,
                                "side": "BUY",
                                "tif": "GTC",
                            }
                        ]
                    )

    def test_protobuf_module_does_not_hand_roll_wire_encoding(self):
        from afx.utils import protobuf

        self.assertFalse(hasattr(protobuf, "_varint"))
        self.assertFalse(hasattr(protobuf, "_key"))


if __name__ == "__main__":
    unittest.main()
