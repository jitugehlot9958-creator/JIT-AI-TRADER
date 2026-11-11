import os
import requests

class DeltaPublicAPI:
    def __init__(self):
        self.base = os.getenv("DELTA_BASE_URL", "https://api.india.delta.exchange").rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", "User-Agent": "JIT-AI-TRADER/1.0"})

    def _get(self, path, params=None):
        response = self.session.get(self.base + path, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
        if payload.get("success") is False:
            raise RuntimeError(str(payload.get("error", "Delta API returned success=false")))
        return payload

    def get_live_perpetual_products(self):
        # Pagination: collect all product pages; filter live perpetual futures.
        all_products, after = [], None
        for _ in range(20):
            params = {"contract_types": "perpetual_futures", "states": "live", "page_size": 100}
            if after:
                params["after"] = after
            data = self._get("/v2/products", params)
            all_products.extend(data.get("result", []))
            after = (data.get("meta") or {}).get("after")
            if not after:
                break
        return [p for p in all_products
                if p.get("state") == "live"
                and (p.get("contract_type") or p.get("product_type")) == "perpetual_futures"
                and p.get("symbol") and p.get("id")]

    def get_tickers(self):
        data = self._get("/v2/tickers", {"contract_types": "perpetual_futures"})
        return data.get("result", [])

    def get_candles(self, symbol, resolution="5m", limit=250):
        import time
        end = int(time.time())
        seconds = {"1m":60, "3m":180, "5m":300, "15m":900, "30m":1800,
                   "1h":3600, "2h":7200, "4h":14400, "6h":21600, "12h":43200, "1d":86400}
        start = end - seconds[resolution] * limit
        data = self._get("/v2/history/candles", {
            "resolution": resolution, "symbol": symbol, "start": start, "end": end
        })
        return data.get("result", [])
