import os
import sys
import time
from decimal import Decimal
from pathlib import Path

from eth_account import Account

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from afx import AfxClient  # noqa: E402


MASTER_ENV = "AFX_E2E_APPROVE_MASTER_PRIVATE_KEY"
AGENT_ENV = "AFX_E2E_APPROVE_AGENT_PRIVATE_KEY"
VALIDITY_SECONDS = 3600


def main():
    suffix = str(int(time.time()))
    master = Account.create()
    agent = Account.create()
    agent_name = f"afx-sdk-approve-{suffix}"

    os.environ[MASTER_ENV] = master.key.hex()
    os.environ[AGENT_ENV] = agent.key.hex()

    print(f"master={master.address}")
    print(f"master_lower={master.address.lower()}")
    print(f"agent={agent.address}")
    print(f"agent_lower={agent.address.lower()}")
    print(f"agent_name={agent_name}")

    client = AfxClient.from_env(
        testnet=True,
        timeout=20,
        master_env=MASTER_ENV,
        agent_env=AGENT_ENV,
    )

    require_success("faucet_claim", client.exchange.faucet_claim())
    wait_for_wallet_balance(client)

    approve = client.exchange.approve_agent(
        agent_name=agent_name,
        validity_seconds=VALIDITY_SECONDS,
    )
    require_success("approve_agent", approve)

    active = wait_for_active_agent(client, agent_name, agent.address)
    print(
        "approve_agent_testnet: ok "
        f"agentName={active.get('agentName')} "
        f"agentAddress={active.get('agentAddress')} "
        f"status={active.get('status')}"
    )


def wait_for_wallet_balance(client, timeout=45):
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = client.info.get_wallet()
        summarize("get_wallet_after_faucet", response)
        data = response.get("data")
        if response.get("code") == 0 and isinstance(data, list) and data:
            balance = Decimal(str(data[0].get("availableBalance", "0")))
            if balance > 0:
                print(f"wallet_available_balance={balance}")
                return
        time.sleep(2)
    raise RuntimeError("wallet balance did not become available after faucet")


def wait_for_active_agent(client, agent_name, expected_address, timeout=45):
    expected = _normalize_address(expected_address)
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = client.info.get_active_agent(agent_name=agent_name)
        summarize("get_active_agent", response)
        data = response.get("data") or {}
        if (
            response.get("code") == 0
            and _normalize_address(data.get("agentAddress")) == expected
            and str(data.get("status")).upper() == "ACTIVE"
        ):
            return data
        time.sleep(2)
    raise RuntimeError(f"agent {agent_name} did not become active")


def require_success(name, response):
    summarize(name, response)
    if response.get("code") != 0:
        raise RuntimeError(f"{name} failed: {response}")
    data = response.get("data")
    if isinstance(data, dict) and data.get("txCode") not in (None, 0):
        raise RuntimeError(f"{name} transaction failed: {response}")


def summarize(name, response):
    code = response.get("code")
    message = response.get("message")
    data = response.get("data")
    print(f"{name}: code={code}, message={message}, data_type={type(data).__name__}")
    if isinstance(data, dict):
        tx_hash = data.get("txHash")
        tx_code = data.get("txCode")
        tx_msg = data.get("txMsg")
        if tx_hash or tx_code is not None or tx_msg:
            print(f"{name}: txHash={tx_hash}, txCode={tx_code}, txMsg={tx_msg}")
        if data.get("agentName") or data.get("agentAddress") or data.get("status"):
            print(
                f"{name}: agentName={data.get('agentName')}, "
                f"agentAddress={data.get('agentAddress')}, "
                f"status={data.get('status')}"
            )
    elif isinstance(data, list):
        print(f"{name}: item_count={len(data)}")


def _normalize_address(address):
    return str(address or "").lower()


if __name__ == "__main__":
    main()
