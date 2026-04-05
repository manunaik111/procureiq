from datetime import datetime


def update_scorecard(scorecard: dict, spend_record: dict) -> dict:
    """
    Update supplier reliability scorecard with a new completed procurement.
    scorecard is a dict keyed by supplier name.
    """
    name = spend_record.get("supplier_name", "Unknown")

    if name not in scorecard:
        scorecard[name] = {
            "supplier_name": name,
            "total_orders": 0,
            "total_spend": 0.0,
            "avg_risk_score": 0.0,
            "avg_savings_pct": 0.0,
            "reliability_score": 1.0,
            "last_used": "",
            "items_supplied": []
        }

    entry = scorecard[name]
    n = entry["total_orders"]

    # Rolling averages
    entry["avg_risk_score"] = round(
        (entry["avg_risk_score"] * n + spend_record["risk_score"]) / (n + 1), 3
    )
    entry["avg_savings_pct"] = round(
        (entry["avg_savings_pct"] * n + spend_record["savings_pct"]) / (n + 1), 2
    )

    entry["total_orders"] += 1
    entry["total_spend"] = round(entry["total_spend"] + spend_record["total_spend"], 2)
    entry["last_used"] = spend_record["completed_at"]

    item = spend_record.get("item", "")
    if item and item not in entry["items_supplied"]:
        entry["items_supplied"].append(item)

    # Reliability score: starts at 1.0, penalised by risk, rewarded by savings
    risk_penalty = entry["avg_risk_score"] * 0.4
    savings_bonus = min(entry["avg_savings_pct"] / 100, 0.2)
    entry["reliability_score"] = round(
        max(0.0, min(1.0, 1.0 - risk_penalty + savings_bonus)), 3
    )

    scorecard[name] = entry
    return scorecard


def get_top_suppliers(scorecard: dict, n: int = 5) -> list:
    """Return top N suppliers by reliability score."""
    entries = list(scorecard.values())
    return sorted(entries, key=lambda x: x["reliability_score"], reverse=True)[:n]


def get_scorecard_summary(scorecard: dict) -> dict:
    """Summary stats across all suppliers."""
    if not scorecard:
        return {"total_suppliers": 0, "avg_reliability": 0.0, "top_supplier": None}

    entries = list(scorecard.values())
    avg_reliability = round(
        sum(e["reliability_score"] for e in entries) / len(entries), 3
    )
    top = max(entries, key=lambda x: x["reliability_score"])

    return {
        "total_suppliers": len(entries),
        "avg_reliability": avg_reliability,
        "top_supplier": top["supplier_name"]
    }