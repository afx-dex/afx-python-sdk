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

    def test_protobuf_module_does_not_hand_roll_wire_encoding(self):
        from afx.utils import protobuf

        self.assertFalse(hasattr(protobuf, "_varint"))
        self.assertFalse(hasattr(protobuf, "_key"))


if __name__ == "__main__":
    unittest.main()
