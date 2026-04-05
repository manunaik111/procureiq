from orchestrator.state import ProcurementState, SupplierInfo
from datetime import datetime
import numpy as np


def score_supplier(supplier: SupplierInfo, market_avg: float) -> float:
    """
    Rule-based risk scorer. Returns 0.0 (safe) to 1.0 (risky).
    Combines the LLM's initial risk estimate with objective metrics.
    """
    score = 0.0

    # Factor 1: LLM initial risk estimate (40% weight)
    score += supplier["risk_score"] * 0.4

    # Factor 2: Price deviation from market average (30% weight)
    if market_avg > 0:
        deviation = abs(supplier["price"] - market_avg) / market_avg
        # More than 40% away from market avg is suspicious
        price_risk = min(deviation / 0.4, 1.0)
        score += price_risk * 0.3

    # Factor 3: Missing URL (20% weight)
    # A real vendor always has a website
    if not supplier.get("url") or supplier["url"] == "":
        score += 0.2

    # Factor 4: Price is zero (10% weight)
    # Could not extract price = transparency issue
    if supplier["price"] <= 0:
        score += 0.1

    return round(min(score, 1.0), 3)


def run_risk_scoring(state: ProcurementState) -> dict:
    log = list(state.get("audit_log", []))
    suppliers = state.get("suppliers", [])
    market_avg = state.get("market_price_avg", 0.0)

    log.append(f"[{datetime.now().isoformat()}] Risk Scoring started for {len(suppliers)} suppliers")

    if not suppliers:
        log.append(f"[{datetime.now().isoformat()}] No suppliers to score — skipping")
        return {
            "suppliers": suppliers,
            "risk_flag": True,
            "audit_log": log
        }

    # Score every supplier
    scored = []
    for s in suppliers:
        final_score = score_supplier(s, market_avg)
        updated = {**s, "risk_score": final_score}
        scored.append(updated)
        log.append(
            f"[{datetime.now().isoformat()}] "
            f"Risk scored: {s['name']} | Final score: {final_score} | "
            f"{'FLAGGED' if final_score >= 0.7 else 'OK'}"
        )

    # Sort by risk score ascending (safest first)
    scored.sort(key=lambda x: x["risk_score"])

    # Overall risk flag — True if ALL suppliers are risky
    risky_count = sum(1 for s in scored if s["risk_score"] >= 0.7)
    risk_flag = risky_count == len(scored)

    log.append(
        f"[{datetime.now().isoformat()}] "
        f"Risk summary: {risky_count}/{len(scored)} suppliers flagged | "
        f"Overall risk flag: {risk_flag}"
    )

    # Best supplier = lowest risk score
    best = scored[0]
    log.append(
        f"[{datetime.now().isoformat()}] "
        f"Best supplier: {best['name']} | Risk: {best['risk_score']} | Price: {best['price']}"
    )

    return {
        "suppliers": scored,
        "selected_supplier": best,
        "risk_flag": risk_flag,
        "audit_log": log
    }