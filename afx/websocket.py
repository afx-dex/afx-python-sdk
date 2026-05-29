import inspect
import json
import time


class WebSocketClient:
    def __init__(self, ws_url, default_user_address=None):
        self.ws_url = ws_url
        self._default_user_address = default_user_address

    async def subscribe(self, subscription, callback=None, timeout=None):
        import websockets

        async with websockets.connect(self.ws_url, close_timeout=5) as ws:
            await ws.send(
                json.dumps({"method": "subscribe", "subscription": subscription})
            )
            return await self._read_messages(ws, callback, timeout)

    async def subscribe_order_book(
        self,
        symbol,
        depth=5,
        callback=None,
        timeout=None,
    ):
        return await self.subscribe(
            {"type": "orderBook", "symbol": symbol, "depth": depth},
            callback=callback,
            timeout=timeout,
        )

    async def subscribe_ticker(self, symbol, callback=None, timeout=None):
        return await self.subscribe(
            {"type": "ticker", "symbol": symbol},
            callback=callback,
            timeout=timeout,
        )

    async def subscribe_account_state(
        self,
        user_address=None,
        callback=None,
        timeout=None,
    ):
        address = user_address or self._default_user_address
        if not address:
            raise ValueError("user_address is required")
        return await self.subscribe(
            {"type": "aopState", "userAddress": address},
            callback=callback,
            timeout=timeout,
        )

    async def _read_messages(self, ws, callback, timeout):
        import asyncio

        started_at = time.monotonic()
        while True:
            wait_timeout = None
            if timeout is not None:
                elapsed = time.monotonic() - started_at
                wait_timeout = max(0.1, timeout - elapsed)
            raw = await asyncio.wait_for(ws.recv(), timeout=wait_timeout)
            message = json.loads(raw)
            if message.get("channel") == "pong":
                continue
            if message.get("method") == "subscribe":
                continue
            if callback is None:
                return message

            result = callback(message)
            if inspect.isawaitable(result):
                result = await result
            if result is False:
                return message
