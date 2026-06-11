from afx.protos import dex_pb2

ORD_TYPE = {
    "LIMIT": dex_pb2.LIMIT,
    "MARKET": dex_pb2.MARKET,
    "STOP_LIMIT": dex_pb2.STOP_LIMIT,
    "STOP_MARKET": dex_pb2.STOP_MARKET,
    "TAKE_PROFIT_LIMIT": dex_pb2.TAKE_PROFIT_LIMIT,
    "TAKE_PROFIT_MARKET": dex_pb2.TAKE_PROFIT_MARKET,
}
DISPLAY_ONLY_ORD_TYPE = {
    "MARKET_LIQ_SELLOFF": dex_pb2.MARKET_LIQ_SELLOFF,
    "LIMIT_LIQ_SELLOFF": dex_pb2.LIMIT_LIQ_SELLOFF,
    "ADL": dex_pb2.ADL,
    "LIQUIDATION": dex_pb2.LIQUIDATION,
}
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
    "NONE": dex_pb2.REDUCE_ONLY_NONE,
    "REDUCE_ONLY": dex_pb2.REDUCE_ONLY,
    "TP_FROM_POSITION": dex_pb2.TP_FROM_POSITION,
    "SL_FROM_POSITION": dex_pb2.SL_FROM_POSITION,
}
TRIGGER_TYPE = {
    "NONE": dex_pb2.TRIGGER_NONE,
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


def replace_order(order):
    return _replace_order(order).SerializeToString()


def place_bracket_order(orders):
    if len(orders) not in (2, 3):
        raise ValueError("place_bracket_order requires 2 or 3 orders")

    message = dex_pb2.MsgPlaceBracketOrder(
        main_order=_place_order(orders[0])
    )
    for order in orders[1:]:
        reduce_only = _enum(
            REDUCE_ONLY_OPTION,
            order.get("reduce_only_option"),
            "reduce_only_option",
        )
        if reduce_only == dex_pb2.TP_FROM_POSITION:
            if message.HasField("take_profit_order"):
                raise ValueError("place_bracket_order accepts only one take profit order")
            message.take_profit_order.CopyFrom(_place_order(order))
        elif reduce_only == dex_pb2.SL_FROM_POSITION:
            if message.HasField("stop_loss_order"):
                raise ValueError("place_bracket_order accepts only one stop loss order")
            message.stop_loss_order.CopyFrom(_place_order(order))
        else:
            raise ValueError(
                "bracket child reduce_only_option must be TP_FROM_POSITION or SL_FROM_POSITION"
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


def vault_deposit(vault_address, amount, currency_code=1):
    return dex_pb2.MsgVaultDeposit(
        vault=vault_address,
        amount=str(amount),
        currency_code=currency_code,
    ).SerializeToString()


def vault_withdraw(vault_address, share, currency_code=1):
    return dex_pb2.MsgVaultWithdraw(
        vault=vault_address,
        share=str(share),
        currency_code=currency_code,
    ).SerializeToString()


def _place_order(order):
    return _order_message(dex_pb2.MsgPlaceOrder, order)


def _replace_order(order):
    message = _order_message(dex_pb2.MsgReplaceOrder, order)
    _set_optional_int(message, "ord_id", order.get("ord_id"))
    return message


def _order_message(message_cls, order):
    message = message_cls(
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
    if name == "ord_type" and _is_display_only_ord_type(value):
        display_only = ", ".join(sorted(DISPLAY_ONLY_ORD_TYPE))
        raise ValueError(
            f"{name} contains display-only values that cannot be used in requests: "
            f"{display_only}"
        )
    if isinstance(value, int):
        if value not in values.values():
            allowed = ", ".join(sorted(values))
            raise ValueError(f"{name} must be one of: {allowed}")
        return value
    try:
        return values[value]
    except KeyError as exc:
        allowed = ", ".join(sorted(values))
        raise ValueError(f"{name} must be one of: {allowed}") from exc


def _is_display_only_ord_type(value):
    if isinstance(value, int):
        return value in DISPLAY_ONLY_ORD_TYPE.values()
    return value in DISPLAY_ONLY_ORD_TYPE
