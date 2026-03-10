import yfinance as yf
import pandas as pd


def get_quote_data(symbol: str) -> dict | None:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or info.get("quoteType") is None:
            return None
        return {
            "ticker": symbol.upper(),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "open": info.get("open") or info.get("regularMarketOpen"),
            "day_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
            "day_low": info.get("dayLow") or info.get("regularMarketDayLow"),
            "volume": info.get("volume") or info.get("regularMarketVolume"),
            "currency": info.get("currency", "USD"),
        }
    except Exception:
        return None


def get_history_data(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame | None:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return None
        return df
    except Exception:
        return None


def get_fundamentals_data(symbol: str) -> dict | None:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or info.get("quoteType") is None:
            return None
        return {
            "ticker": symbol.upper(),
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "description": info.get("longBusinessSummary"),
        }
    except Exception:
        return None


def get_news_data(symbol: str, limit: int = 5) -> list:
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if not news:
            return []
        results = []
        for item in news[:limit]:
            content = item.get("content", {})
            results.append({
                "title": content.get("title"),
                "publisher": content.get("provider", {}).get("displayName"),
                "published_at": content.get("pubDate"),
                "url": content.get("canonicalUrl", {}).get("url"),
            })
        return results
    except Exception:
        return []


FALLBACK_TICKERS = {
    "apple": {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
    "microsoft": {"ticker": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
    "tesla": {"ticker": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
    "amazon": {"ticker": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
    "google": {"ticker": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
    "nvidia": {"ticker": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
    "meta": {"ticker": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
}


def _fallback_search(query: str) -> list:
    query_lower = query.lower()
    return [
        v for k, v in FALLBACK_TICKERS.items()
        if query_lower in k or query_lower in v["ticker"].lower()
    ]


def search_tickers(query: str) -> list:
    try:
        results = yf.Search(query)
        quotes = results.quotes
        if not quotes:
            return _fallback_search(query)
        return [
            {
                "ticker": q.get("symbol"),
                "name": q.get("longname") or q.get("shortname"),
                "exchange": q.get("exchange"),
            }
            for q in quotes
            if q.get("symbol")
        ]
    except Exception:
        return _fallback_search(query)


WATCHLIST = [
    "AAPL", "MSFT", "TSLA", "NVDA", "AMZN", "META", "GOOGL",
    "JPM", "BAC", "XOM", "JNJ", "V", "PG", "HD", "MA",
    "UNH", "DIS", "NFLX", "PYPL", "INTC",
]


def get_movers_data() -> dict | None:
    try:
        tickers_data = yf.download(
            tickers=" ".join(WATCHLIST),
            period="2d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
        )
        movers = []
        for symbol in WATCHLIST:
            try:
                closes = tickers_data[symbol]["Close"].dropna()
                if len(closes) < 2:
                    continue
                prev_close = float(closes.iloc[-2])
                curr_close = float(closes.iloc[-1])
                change_pct = round(((curr_close - prev_close) / prev_close) * 100, 2)
                movers.append({"ticker": symbol, "price": round(curr_close, 2), "change_pct": change_pct})
            except Exception:
                continue

        movers.sort(key=lambda x: x["change_pct"], reverse=True)
        gainers = [m for m in movers if m["change_pct"] > 0][:5]
        losers = sorted([m for m in movers if m["change_pct"] < 0], key=lambda x: x["change_pct"])[:5]
        return {"gainers": gainers, "losers": losers}
    except Exception:
        return None
