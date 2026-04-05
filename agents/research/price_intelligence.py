from prophet import Prophet
from orchestrator.state import ProcurementState
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import random


def generate_synthetic_price_history(base_price: float, days: int = 365) -> pd.DataFrame:
    """Generate realistic price history data for Prophet."""
    random.seed(42)
    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    prices = []
    price = base_price * 0.85

    for i in range(days):
        trend = base_price * 0.0001 * i
        seasonal = base_price * 0.05 * np.sin(2 * np.pi * i / 90)
        noise = random.uniform(-base_price * 0.02, base_price * 0.02)
        price = base_price * 0.85 + trend + seasonal + noise
        prices.append(max(price, base_price * 0.5))

    return pd.DataFrame({"ds": dates, "y": prices})


def run_price_intelligence(state: ProcurementState) -> dict:
    log = list(state.get("audit_log", []))
    market_avg = state.get("market_price_avg", 100.0)

    log.append(f"[{datetime.now().isoformat()}] Price Intelligence started")
    log.append(f"[{datetime.now().isoformat()}] Building price history from market average: {market_avg}")

    df = generate_synthetic_price_history(base_price=market_avg)

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )
    model.fit(df)

    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)

    last = forecast.tail(90)
    forecast_30 = round(float(last.iloc[29]["yhat"]), 2)
    forecast_60 = round(float(last.iloc[59]["yhat"]), 2)
    forecast_90 = round(float(last.iloc[89]["yhat"]), 2)

    trend = "rising" if forecast_90 > market_avg * 1.03 else \
            "falling" if forecast_90 < market_avg * 0.97 else "stable"

    price_forecast = {
        "current_avg": market_avg,
        "forecast_30_days": forecast_30,
        "forecast_60_days": forecast_60,
        "forecast_90_days": forecast_90,
        "trend": trend,
        "recommendation": "Buy now — prices are rising" if trend == "rising"
                          else "Wait — prices are falling" if trend == "falling"
                          else "Buy now — prices are stable"
    }

    log.append(f"[{datetime.now().isoformat()}] Price forecast complete")
    log.append(f"[{datetime.now().isoformat()}] Trend: {trend} | 30d: {forecast_30} | 60d: {forecast_60} | 90d: {forecast_90}")
    log.append(f"[{datetime.now().isoformat()}] Recommendation: {price_forecast['recommendation']}")

    return {
        "price_forecast": price_forecast,
        "audit_log": log,
    }