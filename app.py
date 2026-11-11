import streamlit as st
import pandas as pd
from jit_trader.delta import DeltaPublicAPI
from jit_trader.scanner import scan_universe
from jit_trader.paper import record_paper_trade

st.set_page_config(page_title="JIT AI TRADER", page_icon="📈", layout="wide")
st.title("📈 JIT AI TRADER")
st.caption("Delta Exchange India · Perpetual futures · SMC/ICT-inspired rules · Paper mode")

with st.sidebar:
    st.header("Scanner settings")
    top_n = st.slider("Maximum contracts to analyse", 5, 50, 20, 5)
    timeframe = st.selectbox("Entry timeframe", ["5m", "15m"], index=0)
    min_rr = st.slider("Minimum risk/reward", 1.0, 4.0, 2.0, 0.25)
    st.info("V1.0 is read-only + paper approval. No live orders can be placed.")
    scan = st.button("🔄 Scan market", type="primary", use_container_width=True)

@st.cache_data(ttl=30, show_spinner=False)
def load_universe():
    api = DeltaPublicAPI()
    products = api.get_live_perpetual_products()
    tickers = api.get_tickers()
    return products, tickers

if "signals" not in st.session_state:
    st.session_state.signals = []
if "last_scan" not in st.session_state:
    st.session_state.last_scan = None

try:
    with st.spinner("Loading Delta Exchange perpetual contracts..."):
        products, tickers = load_universe()
    st.metric("Live perpetual contracts found", len(products))
    st.caption("The scanner ranks live contracts by reported volume, then analyses up to the selected maximum.")
    if scan:
        with st.spinner("Downloading candles and checking trend, structure, liquidity and FVG..."):
            st.session_state.signals = scan_universe(products, tickers, top_n, timeframe, min_rr)
            st.session_state.last_scan = pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    st.caption(f"Last scan: {st.session_state.last_scan or 'Not scanned yet'}")

    signals = st.session_state.signals
    if not signals:
        st.info("Press **Scan market** to generate the first set of trade candidates.")
    else:
        df = pd.DataFrame(signals)
        st.subheader("Market scan results")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.subheader("Trade approval (paper only)")
        choices = [f"{s['symbol']} · {s['side']} · score {s['score']}" for s in signals if s["side"] in ("LONG", "SHORT")]
        if choices:
            chosen = st.selectbox("Select a candidate", choices)
            idx = choices.index(chosen)
            candidates = [s for s in signals if s["side"] in ("LONG", "SHORT")]
            candidate = candidates[idx]
            st.json(candidate)
            if st.button("✅ Approve paper trade", type="primary"):
                record_paper_trade(candidate)
                st.success("Paper trade recorded. No real order was sent to Delta Exchange.")
        else:
            st.warning("No qualifying LONG/SHORT setups. WAIT is a valid result.")
    st.subheader("Recent paper approvals")
    if "paper_trades" not in st.session_state:
        st.session_state.paper_trades = []
    if st.session_state.paper_trades:
        st.dataframe(pd.DataFrame(st.session_state.paper_trades), use_container_width=True, hide_index=True)
    else:
        st.caption("No paper approvals yet.")
except Exception as exc:
    st.error(f"Could not load/scan Delta market data: {exc}")
    st.caption("Check internet access, API availability, and try again. This app never submits live orders.")
