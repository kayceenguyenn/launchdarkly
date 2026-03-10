# StockSense API

StockSense is a Python REST API that delivers real-time and historical stock market data using the `yfinance` library. Built as a demonstration of LaunchDarkly's feature management platform, it integrates feature flags and experimentation to control algorithm behavior at runtime — without redeployment.

The project showcases two core LaunchDarkly capabilities:

1. **Feature flagging** — a `price-scoring-algorithm` flag dynamically switches between a simple price score and an advanced VWAP/momentum composite, simulating a safe, controlled algorithm rollout to users.
2. **Experimentation** — a `technical-indicator-algorithm` experiment A/B tests a fast (10-day SMA) vs. slow (50-day SMA) moving average algorithm, with per-request computation time tracked as a metric back to LaunchDarkly's stats engine.

Every API request generates a LaunchDarkly user context from a `user_key` query parameter, meaning different users are independently bucketed into flag variations — exactly as they would be in a production system.

---

## Tech Stack

| Layer           | Technology                     |
| --------------- | ------------------------------ |
| Language        | Python 3.10+                   |
| Framework       | Flask                          |
| Stock Data      | yfinance (Yahoo Finance)       |
| Feature Flags   | LaunchDarkly Python Server SDK |
| Configuration   | python-dotenv                  |
| Data Processing | pandas                         |

---

## Project Structure

```
stocksense/
├── app.py                   # Flask entry point, blueprint registration
├── launchdarkly_client.py   # LaunchDarkly singleton client initialization
├── routes/
│   ├── quote.py             # GET /quote/<ticker>
│   ├── history.py           # GET /history/<ticker>
│   ├── fundamentals.py      # GET /fundamentals/<ticker>
│   ├── news.py              # GET /news/<ticker>
│   ├── search.py            # GET /search
│   ├── indicators.py        # GET /indicators/<ticker>
│   ├── movers.py            # GET /movers
│   └── health.py            # GET /health
├── services/
│   ├── yfinance_service.py  # All yfinance data fetching logic
│   └── scoring.py           # Simple and advanced price scoring algorithms
├── requirements.txt
├── .env.example
└── README.md
```

---

## Prerequisites

- Python 3.10+
- pip
- A LaunchDarkly account with the two flags below configured

---

## Installation

```bash
cd stocksense
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Environment Setup

```bash
cp .env.example .env
```

Open `.env` and set your LaunchDarkly SDK key:

```
LD_SDK_KEY=sdk-your-key-here
PORT=5000
```

To find your SDK key: LaunchDarkly dashboard → **Account Settings** → **Projects** → select your project → **Environments** → copy the **SDK key**.

---

## LaunchDarkly Setup

Two flags must be created in your LaunchDarkly project before starting the server.

### Flag 1: `price-scoring-algorithm`

| Property    | Value                     |
| ----------- | ------------------------- |
| Flag key    | `price-scoring-algorithm` |
| Flag type   | String multivariate       |
| Variation A | `simple` (default)        |
| Variation B | `advanced`                |

Controls the `score` field returned by `GET /quote/<ticker>`.

- `simple` — score equals the last closing price
- `advanced` — score is a weighted composite: `(VWAP × 0.5) + (5-day momentum × 0.3) + (relative volume × 0.2)`

This simulates a real-world scenario: rolling out a more sophisticated pricing model exclusively to premium users without a code deployment. Set up the following targeting rule in the LaunchDarkly dashboard:

- **If** `user_type` **is** `premium` → serve `advanced`
- **Default rule** → serve `simple`

To demo both variations:

```bash
curl "http://127.0.0.1:5000/quote/AAPL?user_key=alice&user_type=premium"   # advanced score
curl "http://127.0.0.1:5000/quote/AAPL?user_key=bob&user_type=free"        # simple score
```

### Flag 2: `technical-indicator-algorithm`

| Property    | Value                           |
| ----------- | ------------------------------- |
| Flag key    | `technical-indicator-algorithm` |
| Flag type   | String multivariate             |
| Variation A | `fast` (default) — 10-day SMA   |
| Variation B | `slow` — 50-day SMA             |

Controls the moving average window used in `GET /indicators/<ticker>`. This flag is the basis of a LaunchDarkly experiment: after computing indicators, the app calls `ldClient.track("indicator-response-time-ms", context, None, elapsed_ms)` to send computation time back to LaunchDarkly, enabling statistically rigorous comparison of which variation performs faster.

---

## Running the Server

```bash
python app.py
```

The server starts at `http://127.0.0.1:5000`. You should see:

```
* Serving Flask app 'app'
* Running on http://127.0.0.1:5000
```

---

## API Reference

### `GET /health`

Confirms the server and LaunchDarkly client are running.

```bash
curl http://127.0.0.1:5000/health
```

```json
{
  "status": "ok",
  "launchdarkly_initialized": true
}
```

---

### `GET /quote/<ticker>`

Returns the current stock quote with a LaunchDarkly-controlled price score.

| Query Param | Type   | Default     | Description                                  |
| ----------- | ------ | ----------- | -------------------------------------------- |
| `user_key`  | string | random UUID | LaunchDarkly context key for flag evaluation |

```bash
curl "http://127.0.0.1:5000/quote/AAPL?user_key=alice"
```

```json
{
  "ticker": "AAPL",
  "price": 213.49,
  "open": 211.2,
  "day_high": 214.3,
  "day_low": 210.85,
  "volume": 54321000,
  "currency": "USD",
  "score": 213.49,
  "score_method": "simple"
}
```

---

### `GET /history/<ticker>`

Returns historical OHLCV (Open, High, Low, Close, Volume) data.

| Query Param | Type   | Default | Valid Values                                      |
| ----------- | ------ | ------- | ------------------------------------------------- |
| `period`    | string | `1mo`   | `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y` |
| `interval`  | string | `1d`    | `1d`, `1wk`, `1mo`                                |

```bash
curl "http://127.0.0.1:5000/history/AAPL?period=3mo&interval=1wk"
```

---

### `GET /fundamentals/<ticker>`

Returns company overview and key financial metrics including market cap, P/E ratio, EPS, dividend yield, and 52-week range.

```bash
curl "http://127.0.0.1:5000/fundamentals/MSFT"
```

---

### `GET /news/<ticker>`

Returns recent news headlines for a ticker.

| Query Param | Type | Default | Description                   |
| ----------- | ---- | ------- | ----------------------------- |
| `limit`     | int  | `5`     | Number of headlines to return |

```bash
curl "http://127.0.0.1:5000/news/TSLA?limit=3"
```

---

### `GET /search`

Autocomplete search for ticker symbols by company name or partial ticker.

| Query Param | Type   | Required | Description                          |
| ----------- | ------ | -------- | ------------------------------------ |
| `q`         | string | yes      | Search query, e.g. `apple` or `AAPL` |

```bash
curl "http://127.0.0.1:5000/search?q=apple"
```

---

### `GET /indicators/<ticker>`

Returns technical indicators (RSI, MACD, SMA). The SMA window is controlled by the `technical-indicator-algorithm` LaunchDarkly experiment, and computation time is tracked as an experiment metric.

```bash
curl "http://127.0.0.1:5000/indicators/NVDA?user_key=alice"
```

```json
{
  "ticker": "NVDA",
  "algorithm_variation": "fast",
  "sma": 211.34,
  "sma_period_days": 10,
  "rsi_14": 58.2,
  "macd": {
    "macd_line": 1.23,
    "signal_line": 0.98,
    "histogram": 0.25
  },
  "computation_time_ms": 143.0
}
```

---

### `GET /movers`

Returns the top 5 gainers and top 5 losers from a watchlist of 20 popular tickers, ranked by daily percentage change.

```bash
curl "http://127.0.0.1:5000/movers"
```

---

## LaunchDarkly Integration Details

### How `ldclient.variation()` works

Every flag evaluation calls:

```python
ld_client.variation("flag-key", context, default_value)
```

- `"flag-key"` — identifies which flag to evaluate
- `context` — the user context (`{"kind": "user", "key": user_key}`), used for consistent bucketing and targeting rules
- `default_value` — returned if the SDK is unavailable or the flag doesn't exist, ensuring the app never crashes due to a flag failure

### Why context matters

LaunchDarkly evaluates flags per-user rather than globally. This means the same flag can return different values for different users simultaneously — enabling gradual rollouts, A/B tests, and targeted releases. In StockSense, each request creates a context from `user_key`, so the same user always gets the same variation (consistent bucketing), while different users can be assigned to different variations.

### How the experiment works

The `technical-indicator-algorithm` experiment uses `ldClient.track()` to send a numeric metric back to LaunchDarkly after each `/indicators` request:

```python
ldClient.track("indicator-response-time-ms", context, None, elapsed_ms)
```

LaunchDarkly's stats engine aggregates these values per variation and determines — with statistical confidence — whether the `fast` or `slow` algorithm has meaningfully different performance. This is a real performance experiment, not a synthetic benchmark.

---

## Error Handling

| Scenario                     | HTTP Status | Response                                 |
| ---------------------------- | ----------- | ---------------------------------------- |
| Unknown ticker               | `404`       | `{"error": "Ticker not found"}`          |
| yfinance network failure     | `503`       | `{"error": "Data source unavailable"}`   |
| Missing required query param | `400`       | `{"error": "Missing required param: q"}` |
| LaunchDarkly SDK failure     | —           | Falls back to default variation silently |
