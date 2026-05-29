from afx.protos import dex_pb2

ORD_TYPE = {"LIMIT": dex_pb2.LIMIT, "MARKET": dex_pb2.MARKET}
ORD_SIDE = {
    "BUY": dex_pb2.BUY,
    "SELL": dex_pb2.SELL,
    "BUY_CLOSE_HEDGE": dex_pb2.BUY_CLOSE_HEDGE,
    "SELL_CLOSE_HEDGE": dex_pb2.SELL_CLOSE_HEDGE,
}
ORD_TIF = {
    "GTC": dex_pb2.GTC,
    "IOC": dex_pb2.IOC,
    "FOK": dex_pb2.FOK,
    "POST_ONLY": dex_pb2.POST_ONLY,
}
REDUCE_ONLY_OPTION = {
    "REDUCE_ONLY": dex_pb2.REDUCE_ONLY,
    "TP_FROM_POSITION": dex_pb2.TP_FROM_POSITION,
    "SL_FROM_POSITION": dex_pb2.SL_FROM_POSITION,
}
TRIGGER_TYPE = {
    "LAST_PRICE": dex_pb2.LAST_PRICE,
    "MARK_PRICE": dex_pb2.MARK_PRICE,
    "INDEX_PRICE": dex_pb2.INDEX_PRICE,
}
MARGIN_MODE = {"CROSS": dex_pb2.CROSS, "ISOLATED": dex_pb2.ISOLATED}


def place_orders(orders):
    message = dex_pb2.MsgPlaceOrders(
        orders=[_place_order(order) for order in orders]
    )
    return message.SerializeToString()


def cancel_orders(cancels):
    message = dex_pb2.MsgCancelOrders(
        orders=[_cancel_order(cancel) for cancel in cancels]
    )
    return message.SerializeToString()


def cancel_all(symbol_code, conditional=False):
    return dex_pb2.MsgCancelAll(
        symbol_code=symbol_code,
        is_conditional_order=conditional,
    ).SerializeToString()


def set_leverage(symbol_code, leverage):
    return dex_pb2.MsgSetLeverage(
        symbol_code=symbol_code,
        leverage=str(leverage),
    ).SerializeToString()


def set_margin_mode(symbol_code, mode):
    return dex_pb2.MsgSetMarginMode(
        symbol_code=symbol_code,
        margin_mode=_enum(MARGIN_MODE, mode, "mode"),
    ).SerializeToString()


def assign_pos_margin(symbol_code, amount):
    return dex_pb2.MsgAssignPosMargin(
        symbol_code=symbol_code,
        assigned_pos_margin=str(amount),
    ).SerializeToString()


def bind_referral(code):
    return dex_pb2.MsgBindReferral(referral_code=code).SerializeToString()


def vault_deposit(amount, currency_code=1):
    return dex_pb2.MsgVaultDeposit(
        amount=str(amount),
        currency_code=currency_code,
    ).SerializeToString()


def vault_withdraw(amount, currency_code=1):
    return dex_pb2.MsgVaultWithdraw(
        amount=str(amount),
        currency_code=currency_code,
    ).SerializeToString()


def _place_order(order):
    message = dex_pb2.MsgPlaceOrder(
        symbol_code=order["symbol_code"],
        ord_px=str(order["px"]),
        ord_qty=str(order["qty"]),
        ord_type=_enum(ORD_TYPE, order["ord_type"], "ord_type"),
        ord_side=_enum(ORD_SIDE, order["side"], "side"),
        time_in_force=_enum(ORD_TIF, order["tif"], "tif"),
    )
    _set_optional_int(message, "cl_ord_id", order.get("cl_ord_id"))
    _set_optional_int(message, "parent_ord_id", order.get("parent_ord_id"))
    _set_optional_str(message, "trigger_px", order.get("trigger_px"))
    _set_optional_str(message, "slippage_pct", order.get("slippage_pct"))
    _set_optional_enum(
        message,
        "reduce_only_option",
        REDUCE_ONLY_OPTION,
        order.get("reduce_only_option"),
        "reduce_only_option",
    )
    _set_optional_enum(
        message,
        "tpsl_trigger_type",
        TRIGGER_TYPE,
        order.get("trigger_type"),
        "trigger_type",
    )
    return message


def _cancel_order(cancel):
    message = dex_pb2.MsgCancelOrder(symbol_code=cancel["symbol_code"])
    _set_optional_int(message, "ord_id", cancel.get("ord_id"))
    _set_optional_int(message, "cl_ord_id", cancel.get("cl_ord_id"))
    return message


def _set_optional_int(message, field, value):
    if value not in (None, 0):
        setattr(message, field, int(value))


def _set_optional_str(message, field, value):
    if value not in (None, ""):
        setattr(message, field, str(value))


def _set_optional_enum(message, field, values, value, name):
    if value is not None:
        setattr(message, field, _enum(values, value, name))


def _enum(values, value, name):
    if isinstance(value, int):
        return value
    try:
        return values[value]
    except KeyError as exc:
        allowed = ", ".join(sorted(values))
        raise ValueError(f"{name} must be one of: {allowed}") from exc
