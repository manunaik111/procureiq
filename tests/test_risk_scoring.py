import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.decision.risk_scoring import score_supplier

def test_low_risk_supplier():
    supplier = {"name": "Honeywell", "url": "https://honeywell.com", "price": 350.0, "risk_score": 0.1, "notes": ""}
    score = score_supplier(supplier, market_avg=350.0)
    assert score < 0.5, f"Expected low risk, got {score}"

def test_high_risk_no_url():
    supplier = {"name": "Unknown", "url": "", "price": 100.0, "risk_score": 0.8, "notes": ""}
    score = score_supplier(supplier, market_avg=350.0)
    assert score >= 0.7, f"Expected high risk, got {score}"

def test_price_deviation_risk():
    supplier = {"name": "Cheap", "url": "https://cheap.com", "price": 50.0, "risk_score": 0.2, "notes": ""}
    score = score_supplier(supplier, market_avg=350.0)
    assert score > 0.3, f"Expected elevated risk for extreme price deviation, got {score}"

def test_score_capped_at_one():
    supplier = {"name": "Bad", "url": "", "price": 0.0, "risk_score": 1.0, "notes": ""}
    score = score_supplier(supplier, market_avg=350.0)
    assert score <= 1.0, f"Score should never exceed 1.0, got {score}"

if __name__ == "__main__":
    test_low_risk_supplier()
    test_high_risk_no_url()
    test_price_deviation_risk()
    test_score_capped_at_one()
    print("All tests passed.")