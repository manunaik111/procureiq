from langchain_groq import ChatGroq
from orchestrator.state import ProcurementState
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def run_negotiation_strategy(state: ProcurementState) -> dict:
    log = list(state.get("audit_log", []))
    supplier = state.get("selected_supplier")
    market_avg = state.get("market_price_avg", 0.0)
    quantity = state.get("quantity", 1)
    budget = state.get("budget", 0.0)
    item = state.get("item", "")
    forecast = state.get("price_forecast", {})

    log.append(f"[{datetime.now().isoformat()}] Negotiation Strategy agent started")

    if not supplier:
        log.append(f"[{datetime.now().isoformat()}] No supplier selected — skipping negotiation")
        return {"negotiation_strategy": "No supplier available", "audit_log": log}

    supplier_price = supplier["price"]
    total_cost = supplier_price * quantity
    budget_per_unit = budget / quantity if quantity > 0 else budget
    trend = forecast.get("trend", "stable")
    forecast_90 = forecast.get("forecast_90_days", market_avg)

    prompt = f"""You are a senior procurement negotiation expert. Analyze this situation and give a negotiation strategy.

PROCUREMENT DETAILS:
- Item: {item}
- Quantity needed: {quantity} units
- Total budget: {budget}
- Budget per unit: {round(budget_per_unit, 2)}

SELECTED SUPPLIER:
- Name: {supplier["name"]}
- Quoted price per unit: {supplier_price}
- Total cost at quoted price: {total_cost}
- Risk score: {supplier["risk_score"]} (0=safe, 1=risky)

MARKET INTELLIGENCE:
- Market average price: {market_avg} per unit
- Price trend: {trend}
- 90-day price forecast: {forecast_90} per unit

Provide a negotiation strategy with these exact sections:
1. BATNA (Best Alternative To a Negotiated Agreement): What we do if talks fail
2. ZOPA (Zone of Possible Agreement): The price range both sides can accept
3. Opening offer: What price to open with and why
4. Target price: The ideal price we want to achieve
5. Walk-away price: The maximum we will pay per unit
6. Tactics: 2-3 specific negotiation tactics for this situation

Keep it practical and specific. Maximum 200 words total."""

    response = llm.invoke(prompt)
    strategy = response.content.strip()

    log.append(f"[{datetime.now().isoformat()}] Negotiation strategy generated for {supplier['name']}")
    log.append(f"[{datetime.now().isoformat()}] Supplier price: {supplier_price} | Market avg: {market_avg} | Gap: {round(supplier_price - market_avg, 2)}")

    return {
        "negotiation_strategy": strategy,
        "audit_log": log
    }