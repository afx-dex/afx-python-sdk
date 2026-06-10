import struct

from eth_hash.auto import keccak


DOMAIN_VERIFYING_CONTRACT = "0x0100000000000000000000000000000000000001"

EIP712_DOMAIN_TYPE = [
    {"name": "name", "type": "string"},
    {"name": "version", "type": "string"},
    {"name": "chainId", "type": "uint256"},
    {"name": "verifyingContract", "type": "address"},
]

AGENT_TYPE = [
    {"name": "source", "type": "string"},
    {"name": "connectionId", "type": "bytes32"},
]

APPROVE_AGENT_TYPE = [
    {"name": "dexChain", "type": "string"},
    {"name": "agentAddress", "type": "address"},
    {"name": "agentName", "type": "string"},
    {"name": "validitySeconds", "type": "uint64"},
    {"name": "nonce", "type": "uint64"},
    {"name": "expiryAfter", "type": "uint64"},
]

WITHDRAW_TYPE = [
    {"name": "dexChain", "type": "string"},
    {"name": "destination", "type": "address"},
    {"name": "amount", "type": "string"},
    {"name": "withdrawSequence", "type": "uint64"},
    {"name": "nonce", "type": "uint64"},
    {"name": "expiryAfter", "type": "uint64"},
]

FAUCET_CLAIM_TYPE = [
    {"name": "dexChain", "type": "string"},
]


def build_connection_id(proto_bytes, vault_address, nonce, expiry_after):
    expiry_after = int(expiry_after or 0)
    payload = bytearray(proto_bytes)

    if vault_address:
        payload.extend(bytes.fromhex(vault_address.removeprefix("0x")))

    payload.extend(struct.pack("<Q", int(nonce)))
    payload.extend(struct.pack("<Q", expiry_after))
    return keccak(bytes(payload))


def sign_agent_payload(
    wallet,
    environment,
    proto_bytes,
    nonce,
    expiry_after=None,
    vault_address=None,
):
    connection_id = build_connection_id(
        proto_bytes=proto_bytes,
        vault_address=vault_address,
        nonce=nonce,
        expiry_after=expiry_after,
    )
    return _signature_to_dict(
        wallet.sign_with_agent(
            _typed_message(
                primary_type="Agent",
                type_fields=AGENT_TYPE,
                domain=_domain("Exchange", environment.chain_id),
                message={
                    "source": environment.source,
                    "connectionId": "0x" + connection_id.hex(),
                },
            )
        )
    )


def sign_master_payload(
    wallet,
    environment,
    primary_type,
    type_fields,
    message,
):
    return _signature_to_dict(
        wallet.sign_with_master(
            _typed_message(
                primary_type=primary_type,
                type_fields=type_fields,
                domain=_domain("SignTransaction", environment.chain_id),
                message=message,
            )
        )
    )


def _domain(name, chain_id):
    return {
        "name": name,
        "version": "1",
        "chainId": chain_id,
        "verifyingContract": DOMAIN_VERIFYING_CONTRACT,
    }


def _typed_message(primary_type, type_fields, domain, message):
    return {
        "types": {
            "EIP712Domain": EIP712_DOMAIN_TYPE,
            primary_type: type_fields,
        },
        "primaryType": primary_type,
        "domain": domain,
        "message": message,
    }


def _signature_to_dict(signed):
    return {
        "r": "0x" + format(signed.r, "064x"),
        "s": "0x" + format(signed.s, "064x"),
        "v": signed.v,
    }
