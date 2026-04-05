from datetime import datetime
from orchestrator.state import ProcurementState


def calculate_savings(supplier_price: float, market_avg: float, quantity: int) -> dict:
    """Calculate savings vs market average."""
    if market_avg <= 0:
        return {"savings_per_unit": 0.0, "total_savings": 0.0, "savings_pct": 0.0}

    savings_per_unit = round(market_avg - supplier_price, 2)
    total_savings = round(savings_per_unit * quantity, 2)
    savings_pct = round((savings_per_unit / market_avg) * 100, 2)

    return {
        "savings_per_unit": savings_per_unit,
        "total_savings": total_savings,
        "savings_pct": savings_pct
    }


def build_spend_record(state: ProcurementState) -> dict:
    """Build a spend analytics record from a completed workflow."""
    supplier = state.get("selected_supplier") or {}
    forecast = state.get("price_forecast") or {}
    quantity = state.get("quantity", 0)
    market_avg = state.get("market_price_avg", 0.0)
    supplier_price = supplier.get("price", 0.0)

    savings = calculate_savings(supplier_price, market_avg, quantity)

    return {
        "request_id": state.get("request_id", ""),
        "item": state.get("item", ""),
        "quantity": quantity,
        "budget": state.get("budget", 0.0),
        "supplier_name": supplier.get("name", "Unknown"),
        "supplier_price": supplier_price,
        "market_avg_price": market_avg,
        "total_spend": round(supplier_price * quantity, 2),
        "savings_per_unit": savings["savings_per_unit"],
        "total_savings": savings["total_savings"],
        "savings_pct": savings["savings_pct"],
        "price_trend": forecast.get("trend", "unknown"),
        "risk_score": supplier.get("risk_score", 0.0),
        "decision": state.get("decision", ""),
        "po_number": state.get("po_number", ""),
        "completed_at": state.get("completed_at") or datetime.now().isoformat(),
    }


def summarize_spend(records: list[dict]) -> dict:
    """Summarize a list of spend records into KPIs."""
    if not records:
        return {
            "total_requests": 0,
            "total_spend": 0.0,
            "total_savings": 0.0,
            "avg_savings_pct": 0.0,
            "avg_risk_score": 0.0,
            "decisions": {"buy": 0, "wait": 0, "escalate": 0},
            "top_suppliers": [],
            "spend_by_item": {}
        }

    total_spend = sum(r["total_spend"] for r in records)
    total_savings = sum(r["total_savings"] for r in records)
    avg_savings_pct = round(sum(r["savings_pct"] for r in records) / len(records), 2)
    avg_risk = round(sum(r["risk_score"] for r in records) / len(records), 3)

    decisions = {"buy": 0, "wait": 0, "escalate": 0}
    for r in records:
        d = r.get("decision", "")
        if d in decisions:
            decisions[d] += 1

    supplier_spend = {}
    for r in records:
        name = r["supplier_name"]
        supplier_spend[name] = supplier_spend.get(name, 0) + r["total_spend"]
    top_suppliers = sorted(supplier_spend.items(), key=lambda x: x[1], reverse=True)[:5]

    spend_by_item = {}
    for r in records:
        item = r["item"]
        spend_by_item[item] = spend_by_item.get(item, 0) + r["total_spend"]

    return {
        "total_requests": len(records),
        "total_spend": round(total_spend, 2),
        "total_savings": round(total_savings, 2),
        "avg_savings_pct": avg_savings_pct,
        "avg_risk_score": avg_risk,
        "decisions": decisions,
        "top_suppliers": top_suppliers,
        "spend_by_item": spend_by_item
    }