# JIT AI TRADER V1.0

Android-friendly Streamlit dashboard for Delta Exchange India perpetual futures.

## Included in V1.0
- Fetches live perpetual product catalog from Delta Exchange.
- Ranks contracts using available ticker volume fields.
- Downloads candle history and runs a transparent rule-based first-pass scanner.
- EMA 9/15/50/200, recent swing sweep, close-confirmed structure break, and 3-candle FVG approximation.
- Shows LONG / SHORT / WAIT candidates with illustrative stop and target levels.
- Paper approval log only. **No live order endpoint, API key, or order execution is included.**

## Important limitations
- This is a starter prototype, not a validated profitable strategy.
- BOS/CHoCH, order blocks, liquidity and FVG need more rigorous pivot/structure definitions and backtesting before use.
- V1 scans up to the selected number of highest-volume live perpetual contracts, not every contract on every scan. Increase the cap or build a scheduled batch scanner for full-universe coverage.
- The current risk/reward setting is a target multiple, not a guarantee of execution price or fill.
- No multi-timeframe confirmation, funding/OI filters, fees, slippage, liquidation modelling, or exchange contract-size conversion yet.
- Do not use real capital based on this prototype.

## Run locally
1. Install Python 3.11+.
2. Unzip the project.
3. Create and activate a virtual environment.
4. Install dependencies:
   `pip install -r requirements.txt`
5. Run:
   `streamlit run app.py`
6. Open the shown URL in Chrome. On Android, use the computer/cloud-hosted URL.

## Deploy for Android access
Deploy this repository to a trusted Python hosting service that supports Streamlit. Keep the service running and open its HTTPS URL in Android Chrome. Do not put API secrets in source code or public repositories.

## Delta API
Uses public endpoints documented at https://docs.delta.exchange/:
- GET /v2/products
- GET /v2/tickers
- GET /v2/history/candles

The India production market-data base URL is `https://api.india.delta.exchange`. Public market data does not need account API credentials.

## Roadmap before any live trading
1. Add multi-timeframe structure engine and precise swing pivots.
2. Add backtest engine with fees, slippage, funding, and contract multipliers.
3. Add persistent database and alert delivery.
4. Add secure manual approval with expiring one-time trade tokens.
5. Add Delta demo-account execution and verify bracket/stop behaviour.
6. Only after extensive testing, consider live execution with a separate restricted API key and hard risk limits.
