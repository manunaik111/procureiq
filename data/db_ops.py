from data.models import (
    get_session, init_db,
    ProcurementRecord, SupplierRecord, SpendRecord
)
from orchestrator.state import ProcurementState
from intelligence.spend_analytics import build_spend_record


def save_procurement(state: ProcurementState):
    """Save a completed procurement to PostgreSQL."""
    try:
        session = get_session()
        request_id = state.get("request_id", "")

        # Check if already exists
        existing = session.query(ProcurementRecord).filter_by(
            request_id=request_id
        ).first()

        if existing:
            existing.decision       = state.get("decision", "")
            existing.po_number      = state.get("po_number", "")
            existing.rfq_reference  = f"RFQ-{request_id[:8].upper()}"
            existing.contract_ref   = f"CON-{request_id[:8].upper()}"
            existing.human_approved = state.get("human_approved", False)
            existing.approver_notes = state.get("approver_notes", "")
            existing.completed_at   = state.get("completed_at", "")
            existing.audit_log      = state.get("audit_log", [])
        else:
            record = ProcurementRecord(
                request_id      = request_id,
                item            = state.get("item", ""),
                quantity        = state.get("quantity", 0),
                budget          = state.get("budget", 0.0),
                deadline        = state.get("deadline", ""),
                decision        = state.get("decision", ""),
                po_number       = state.get("po_number", ""),
                rfq_reference   = f"RFQ-{request_id[:8].upper()}",
                contract_ref    = f"CON-{request_id[:8].upper()}",
                human_approved  = state.get("human_approved", False),
                approver_notes  = state.get("approver_notes", ""),
                created_at      = state.get("created_at", ""),
                completed_at    = state.get("completed_at", ""),
                audit_log       = state.get("audit_log", [])
            )
            session.add(record)

        # Save all suppliers
        suppliers = state.get("suppliers", [])
        selected = state.get("selected_supplier") or {}
        for s in suppliers:
            supplier_rec = SupplierRecord(
                request_id  = request_id,
                name        = s.get("name", ""),
                url         = s.get("url", ""),
                price       = s.get("price", 0.0),
                risk_score  = s.get("risk_score", 0.0),
                notes       = s.get("notes", ""),
                selected    = s.get("name") == selected.get("name")
            )
            session.add(supplier_rec)

        # Save spend record
        spend = build_spend_record(state)
        spend_rec = SpendRecord(
            request_id      = request_id,
            item            = spend["item"],
            quantity        = spend["quantity"],
            supplier_name   = spend["supplier_name"],
            supplier_price  = spend["supplier_price"],
            market_avg      = spend["market_avg_price"],
            total_spend     = spend["total_spend"],
            total_savings   = spend["total_savings"],
            savings_pct     = spend["savings_pct"],
            risk_score      = spend["risk_score"],
            price_trend     = spend["price_trend"],
            po_number       = spend["po_number"],
            completed_at    = spend["completed_at"]
        )
        session.add(spend_rec)

        session.commit()
        session.close()
        print(f"Saved procurement {request_id[:8].upper()} to database")
        return True

    except Exception as e:
        print(f"DB save failed: {e}")
        return False


def get_all_procurements() -> list:
    """Fetch all completed procurements from DB."""
    try:
        session = get_session()
        records = session.query(ProcurementRecord).all()
        result = []
        for r in records:
            result.append({
                "request_id":     r.request_id,
                "item":           r.item,
                "quantity":       r.quantity,
                "budget":         r.budget,
                "decision":       r.decision,
                "po_number":      r.po_number,
                "human_approved": r.human_approved,
                "created_at":     r.created_at,
                "completed_at":   r.completed_at,
            })
        session.close()
        return result
    except Exception as e:
        print(f"DB fetch failed: {e}")
        return []


def get_all_spend_records() -> list:
    """Fetch all spend records for analytics."""
    try:
        session = get_session()
        records = session.query(SpendRecord).all()
        result = []
        for r in records:
            result.append({
                "item":           r.item,
                "quantity":       r.quantity,
                "supplier_name":  r.supplier_name,
                "supplier_price": r.supplier_price,
                "market_avg":     r.market_avg,
                "total_spend":    r.total_spend,
                "total_savings":  r.total_savings,
                "savings_pct":    r.savings_pct,
                "risk_score":     r.risk_score,
                "price_trend":    r.price_trend,
                "po_number":      r.po_number,
                "completed_at":   r.completed_at
            })
        session.close()
        return result
    except Exception as e:
        print(f"DB fetch failed: {e}")
        return []