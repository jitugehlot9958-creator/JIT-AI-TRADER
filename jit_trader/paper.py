import streamlit as st
from datetime import datetime, timezone

def record_paper_trade(candidate):
    if "paper_trades" not in st.session_state:
        st.session_state.paper_trades = []
    item = dict(candidate)
    item["approved_at"] = datetime.now(timezone.utc).isoformat()
    item["mode"] = "PAPER_ONLY"
    st.session_state.paper_trades.insert(0, item)
