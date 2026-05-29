class InfoClient:
    def __init__(self, transport, default_user_address=None):
        self._transport = transport
        self._default_user_address = default_user_address

    def get_products(self):
        return self._transport.get("/info/public/product-meta")

    def get_wallet(self, user_addr=None, currency=None, include_zero=False):
        params = {"userAddr": self._user_addr(user_addr)}
        if currency is not None:
            params["currency"] = currency
        if include_zero:
            params["includeZero"] = True
        return self._transport.get("/info/account/wallet", params)

    def get_agents(
        self,
        user_addr=None,
        role=None,
        status=None,
        agent_address=None,
        master_address=None,
        page=None,
        page_size=None,
    ):
        params = {"userAddr": self._user_addr(user_addr)}
        _optional(params, "role", role)
        _optional(params, "status", status)
        _optional(params, "agentAddress", agent_address)
        _optional(params, "masterAddress", master_address)
        _optional(params, "page", page)
        _optional(params, "pageSize", page_size)
        return self._transport.get("/info/account/agent", params)

    def get_active_agent(self, agent_name, user_addr=None):
        return self._transport.get(
            "/info/account/agent/active",
            {
                "userAddr": self._user_addr(user_addr),
                "agentName": agent_name,
            },
        )

    def get_orders(self, user_addr=None, symbol=None, status=None):
        params = {"userAddr": self._user_addr(user_addr)}
        if symbol is not None:
            params["symbol"] = symbol
        if status is not None:
            params["status"] = status
        return self._transport.get("/info/order/states", params)

    def get_positions(self, user_addr=None):
        return self._transport.get(
            "/info/position/list",
            {"userAddr": self._user_addr(user_addr)},
        )

    def get_kline(self, symbol_name, interval, limit=100):
        return self._transport.get(
            "/info/kline/last",
            {
                "symbol_name": symbol_name,
                "interval": interval,
                "limit": limit,
            },
        )

    def get_funding_rate_current(self, symbol=None):
        params = {}
        if symbol is not None:
            params["symbol"] = symbol
        return self._transport.get("/info/fundingRate/current", params)

    def _user_addr(self, user_addr):
        resolved = user_addr or self._default_user_address
        if not resolved:
            raise ValueError("user_addr is required")
        return resolved


def _optional(target, key, value):
    if value is not None:
        target[key] = value
