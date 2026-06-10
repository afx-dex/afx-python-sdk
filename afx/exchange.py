import time

from afx.utils import protobuf
from afx.utils.signing import (
    APPROVE_AGENT_TYPE,
    FAUCET_CLAIM_TYPE,
    WITHDRAW_TYPE,
    sign_agent_payload,
    sign_master_payload,
)


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


class ExchangeClient:
    def __init__(self, transport, environment, wallet):
        self._transport = transport
        self._environment = environment
        self._wallet = wallet
        self._last_nonce = 0

    def faucet_claim(self, nonce=None):
        if self._environment.dex_chain != "Testnet":
            raise ValueError("faucet_claim is only available on testnet")
        nonce = self._nonce(nonce)
        action = {"type": "faucetClaim"}
        signature = sign_master_payload(
            self._wallet,
            self._environment,
            "TestnetFaucetClaim",
            FAUCET_CLAIM_TYPE,
            {"dexChain": "Testnet"},
        )
        return self._post(action, signature, nonce)

    def approve_agent(
        self,
        agent_name="app.afx.xyz",
        validity_seconds=0,
        agent_address=None,
        expiry_seconds=300,
        nonce=None,
        expiry_after=None,
    ):
        nonce = self._nonce(nonce)
        expiry_after = self._expiry_after(expiry_after, expiry_seconds)
        agent_address = agent_address or self._wallet.agent_address
        action = {
            "type": "approveAgent",
            "agentAddress": agent_address,
            "agentName": agent_name,
            "validitySeconds": validity_seconds,
            "dexChain": self._environment.dex_chain,
        }
        signature = sign_master_payload(
            self._wallet,
            self._environment,
            "ApproveAgent",
            APPROVE_AGENT_TYPE,
            {
                "dexChain": self._environment.dex_chain,
                "agentAddress": agent_address,
                "agentName": agent_name,
                "validitySeconds": validity_seconds,
                "nonce": nonce,
                "expiryAfter": int(expiry_after or 0),
            },
        )
        return self._post(action, signature, nonce, expiry_after=expiry_after)

    def revoke_agent(
        self,
        agent_name="app.afx.xyz",
        expiry_seconds=300,
        nonce=None,
        expiry_after=None,
    ):
        return self.approve_agent(
            agent_name=agent_name,
            validity_seconds=0,
            agent_address=ZERO_ADDRESS,
            expiry_seconds=expiry_seconds,
            nonce=nonce,
            expiry_after=expiry_after,
        )

    def withdraw(
        self,
        destination,
        amount,
        withdraw_sequence=None,
        expiry_seconds=3600,
        nonce=None,
        expiry_after=None,
    ):
        nonce = self._nonce(nonce)
        withdraw_sequence = int(withdraw_sequence if withdraw_sequence is not None else nonce)
        expiry_after = self._expiry_after(expiry_after, expiry_seconds)
        action = {
            "type": "withdraw",
            "destination": destination,
            "amount": str(amount),
            "withdrawSequence": withdraw_sequence,
        }
        signature = sign_master_payload(
            self._wallet,
            self._environment,
            "Withdraw",
            WITHDRAW_TYPE,
            {
                "dexChain": self._environment.dex_chain,
                "destination": destination,
                "amount": str(amount),
                "withdrawSequence": withdraw_sequence,
                "nonce": nonce,
                "expiryAfter": int(expiry_after or 0),
            },
        )
        return self._post(action, signature, nonce, expiry_after=expiry_after)

    def place_order(
        self,
        symbol_code,
        px,
        qty,
        side="BUY",
        ord_type="LIMIT",
        tif="GTC",
        reduce_only_option=None,
        trigger_px=None,
        trigger_type=None,
        slippage_pct=None,
        cl_ord_id=None,
        parent_ord_id=None,
        nonce=None,
        expiry_after=None,
        vault_address=None,
    ):
        order = {
            "symbol_code": symbol_code,
            "px": px,
            "qty": qty,
            "side": side,
            "ord_type": ord_type,
            "tif": tif,
            "reduce_only_option": reduce_only_option,
            "trigger_px": trigger_px,
            "trigger_type": trigger_type,
            "slippage_pct": slippage_pct,
            "cl_ord_id": cl_ord_id,
            "parent_ord_id": parent_ord_id,
        }
        action_order = {
            "symbolCode": symbol_code,
            "ordPx": str(px),
            "ordQty": str(qty),
            "ordType": ord_type,
            "ordSide": side,
            "timeInForce": tif,
        }
        _optional(action_order, "reduceOnlyOption", reduce_only_option)
        _optional(action_order, "triggerPx", trigger_px)
        _optional(action_order, "tpslTriggerType", trigger_type)
        _optional(action_order, "slippagePct", slippage_pct)
        _optional(action_order, "clOrdId", cl_ord_id)
        _optional(action_order, "parentOrdId", parent_ord_id)
        return self._agent_request(
            {"type": "placeOrder", "orders": [action_order]},
            protobuf.place_orders([order]),
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def cancel_order(
        self,
        symbol_code,
        ord_id=None,
        cl_ord_id=None,
        nonce=None,
        expiry_after=None,
        vault_address=None,
    ):
        if ord_id is None and cl_ord_id is None:
            raise ValueError("ord_id or cl_ord_id is required")
        cancel = {
            "symbol_code": symbol_code,
            "ord_id": ord_id,
            "cl_ord_id": cl_ord_id,
        }
        action_cancel = {"symbolCode": symbol_code}
        _optional(action_cancel, "ordId", str(ord_id) if ord_id is not None else None)
        _optional(
            action_cancel,
            "clOrdId",
            str(cl_ord_id) if cl_ord_id is not None else None,
        )
        return self._agent_request(
            {"type": "cancelOrder", "cancels": [action_cancel]},
            protobuf.cancel_orders([cancel]),
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def cancel_all(
        self,
        symbol_code,
        conditional=False,
        nonce=None,
        expiry_after=None,
        vault_address=None,
    ):
        return self._agent_request(
            {
                "type": "cancelAll",
                "symbolCode": symbol_code,
                "conditionalOrder": conditional,
            },
            protobuf.cancel_all(symbol_code, conditional),
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def set_leverage(
        self,
        symbol_code,
        leverage,
        nonce=None,
        expiry_after=None,
        vault_address=None,
    ):
        return self._agent_request(
            {
                "type": "setLeverage",
                "symbolCode": symbol_code,
                "leverage": str(leverage),
            },
            protobuf.set_leverage(symbol_code, leverage),
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def set_margin_mode(
        self,
        symbol_code,
        mode,
        nonce=None,
        expiry_after=None,
        vault_address=None,
    ):
        return self._agent_request(
            {
                "type": "setMarginMode",
                "symbolCode": symbol_code,
                "marginMode": mode,
            },
            protobuf.set_margin_mode(symbol_code, mode),
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def assign_pos_margin(
        self,
        symbol_code,
        amount,
        nonce=None,
        expiry_after=None,
        vault_address=None,
    ):
        return self._agent_request(
            {
                "type": "assignPosMargin",
                "symbolCode": symbol_code,
                "assignedPosMargin": str(amount),
            },
            protobuf.assign_pos_margin(symbol_code, amount),
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def bind_referral(self, code, nonce=None, expiry_after=None, vault_address=None):
        return self._agent_request(
            {"type": "bindReferral", "referralCode": code},
            protobuf.bind_referral(code),
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def vault_deposit(
        self,
        vault_address,
        amount,
        currency_code=1,
        nonce=None,
        expiry_after=None,
    ):
        return self._agent_request(
            {
                "type": "vaultDeposit",
                "amount": str(amount),
                "currencyCode": currency_code,
            },
            protobuf.vault_deposit(amount, currency_code),
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def vault_withdraw(
        self,
        vault_address,
        amount,
        currency_code=1,
        nonce=None,
        expiry_after=None,
    ):
        return self._agent_request(
            {
                "type": "vaultWithdraw",
                "amount": str(amount),
                "currencyCode": currency_code,
            },
            protobuf.vault_withdraw(amount, currency_code),
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def _agent_request(
        self,
        action,
        proto_bytes,
        nonce=None,
        expiry_after=None,
        vault_address=None,
    ):
        nonce = self._nonce(nonce)
        signature = sign_agent_payload(
            self._wallet,
            self._environment,
            proto_bytes=proto_bytes,
            nonce=nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )
        return self._post(
            action,
            signature,
            nonce,
            expiry_after=expiry_after,
            vault_address=vault_address,
        )

    def _post(
        self,
        action,
        signature,
        nonce,
        expiry_after=None,
        vault_address=None,
    ):
        body = {
            "action": action,
            "signature": signature,
            "nonce": nonce,
        }
        if expiry_after is not None:
            body["expiryAfter"] = expiry_after
        if vault_address is not None:
            body["vaultAddress"] = vault_address
        return self._transport.post("/api/v1/exchange", body)

    def _nonce(self, nonce):
        if nonce is not None:
            return int(nonce)
        current = int(time.time() * 1000)
        if current <= self._last_nonce:
            current = self._last_nonce + 1
        self._last_nonce = current
        return current

    def _expiry_after(self, expiry_after, expiry_seconds):
        if expiry_after is not None:
            return int(expiry_after)
        if expiry_seconds is None:
            return None
        return int(time.time() * 1000) + int(expiry_seconds) * 1000


def _optional(target, key, value):
    if value is not None:
        target[key] = value
