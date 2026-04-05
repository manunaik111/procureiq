from typing import TypedDict, Optional, List


class SupplierInfo(TypedDict):
    name: str
    url: str
    price: float
    risk_score: float
    notes: str


class ProcurementState(TypedDict):
    # Input
    request_id: str
    item: str
    quantity: int
    budget: float
    deadline: str

    # Research layer
    suppliers: List[SupplierInfo]
    market_price_avg: float
    price_forecast: dict

    # Decision layer
    selected_supplier: Optional[SupplierInfo]
    risk_flag: bool
    negotiation_strategy: str
    decision: str                  # "buy" | "wait" | "escalate"

    # Human gate
    human_approved: bool
    approver_notes: str

    # Document layer
    rfq_text: str
    contract_text: str
    po_number: str

    # Audit
    created_at: str
    completed_at: Optional[str]
    audit_log: List[str]