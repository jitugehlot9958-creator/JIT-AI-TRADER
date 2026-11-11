import numpy as np
import pandas as pd

def prepare_frame(rows):
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    # Delta candle keys: time, open, high, low, close, volume.
    aliases = {"o":"open", "h":"high", "l":"low", "c":"close", "v":"volume"}
    df = df.rename(columns=aliases)
    needed = ["open", "high", "low", "close"]
    if not all(c in df.columns for c in needed):
        return pd.DataFrame()
    for c in needed + (["volume"] if "volume" in df.columns else []):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=needed).sort_values("time" if "time" in df.columns else "close")
    return df.reset_index(drop=True)

def analyse(rows, min_rr=2.0):
    df = prepare_frame(rows)
    if len(df) < 60:
        return {"side":"WAIT", "score":0, "reason":"Insufficient candle history"}
    c, h, l = df.close, df.high, df.low
    ema9, ema15 = c.ewm(span=9).mean(), c.ewm(span=15).mean()
    ema50, ema200 = c.ewm(span=50).mean(), c.ewm(span=200).mean()
    last = df.iloc[-1]
    prev = df.iloc[-2]
    recent_high = h.iloc[-21:-1].max()
    recent_low = l.iloc[-21:-1].min()

    # Rule-based approximations: pivots/sweeps and close-confirmed structure break.
    bullish_sweep = last.low < recent_low and last.close > recent_low
    bearish_sweep = last.high > recent_high and last.close < recent_high
    bullish_bos = last.close > recent_high
    bearish_bos = last.close < recent_low
    bullish_fvg = len(df) >= 3 and df.low.iloc[-1] > df.high.iloc[-3]
    bearish_fvg = len(df) >= 3 and df.high.iloc[-1] < df.low.iloc[-3]

    long_score = sum([
        ema9.iloc[-1] > ema15.iloc[-1],
        ema15.iloc[-1] > ema50.iloc[-1],
        ema50.iloc[-1] > ema200.iloc[-1],
        bullish_sweep, bullish_bos, bullish_fvg
    ])
    short_score = sum([
        ema9.iloc[-1] < ema15.iloc[-1],
        ema15.iloc[-1] < ema50.iloc[-1],
        ema50.iloc[-1] < ema200.iloc[-1],
        bearish_sweep, bearish_bos, bearish_fvg
    ])

    side, score = ("LONG", long_score) if long_score > short_score else ("SHORT", short_score)
    if score < 4:
        return {"side":"WAIT", "score":int(max(long_score, short_score)),
                "price":float(last.close), "reason":"Confluence threshold not met"}
    entry = float(last.close)
    # Stop is beyond the recent local extreme with a small volatility-aware buffer.
    atr = float((h-l).rolling(14).mean().iloc[-1])
    if not np.isfinite(atr) or atr <= 0:
        return {"side":"WAIT", "score":int(score), "reason":"ATR unavailable"}
    if side == "LONG":
        sl = min(float(l.iloc[-10:].min()), entry - atr * 1.2)
        risk = entry - sl
        tp1, tp2 = entry + risk * min_rr, entry + risk * min_rr * 1.5
    else:
        sl = max(float(h.iloc[-10:].max()), entry + atr * 1.2)
        risk = sl - entry
        tp1, tp2 = entry - risk * min_rr, entry - risk * min_rr * 1.5
    if risk <= 0:
        return {"side":"WAIT", "score":int(score), "reason":"Invalid stop distance"}
    return {"side":side, "score":int(score), "price":round(entry, 8),
            "stop_loss":round(sl, 8), "target_1":round(tp1, 8), "target_2":round(tp2, 8),
            "risk_reward":float(min_rr), "reason":"EMA + structure/sweep/FVG rule confluence"}
