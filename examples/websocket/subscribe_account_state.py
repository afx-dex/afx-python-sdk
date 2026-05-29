import asyncio

from afx import AfxClient


async def main():
    client = AfxClient.from_env(testnet=True)
    message = await client.websocket.subscribe_account_state(timeout=10)
    print(message)


asyncio.run(main())
