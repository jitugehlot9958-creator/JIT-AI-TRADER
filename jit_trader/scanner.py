from .delta import DeltaPublicAPI
from .strategy import analyse

def _num(x):
    try: return float(x or 0)
    except (TypeError, ValueError): return 0.0

def scan_universe(products, tickers, top_n=20, timeframe="5m", min_rr=2.0):
    ticker_map = {t.get("symbol"): t for t in tickers}
    ranked = []
    for p in products:
        t = ticker_map.get(p.get("symbol"), {})
        volume = _num(t.get("volume") or t.get("turnover") or t.get("quote_volume"))
        ranked.append((volume, p))
    ranked.sort(key=lambda x: x[0], reverse=True)
    api = DeltaPublicAPI()
    output = []
    for volume, product in ranked[:top_n]:
        symbol = product["symbol"]
        try:
            rows = api.get_candles(symbol, timeframe, 250)
            result = analyse(rows, min_rr)
            output.append({
                "symbol": symbol, "side": result.get("side", "WAIT"),
                "score": result.get("score", 0), "last_price": result.get("price"),
                "stop_loss": result.get("stop_loss"), "target_1": result.get("target_1"),
                "target_2": result.get("target_2"), "risk_reward": result.get("risk_reward"),
                "volume_rank_metric": round(volume, 2), "reason": result.get("reason", "")
            })
        except Exception as exc:
            output.append({"symbol":symbol, "side":"ERROR", "score":0, "reason":str(exc)[:140]})
    return output
