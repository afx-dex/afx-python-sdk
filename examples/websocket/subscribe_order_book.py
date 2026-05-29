import asyncio

from afx import AfxClient


async def main():
    client = AfxClient.from_env(testnet=True)
    message = await client.websocket.subscribe_order_book(
        symbol="BTCUSDC",
        depth=5,
        timeout=10,
    )
    print(message)


asyncio.run(main())
