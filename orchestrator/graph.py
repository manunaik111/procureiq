from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from orchestrator.state import ProcurementState
from datetime import datetime
from dotenv import load_dotenv
import uuid
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def research_node(state: ProcurementState) -> dict:
    from agents.research.supplier_discovery import run_supplier_discovery
    from agents.research.price_intelligence import run_price_intelligence

    state = {**state, **run_supplier_discovery(state)}
    state = {**state, **run_price_intelligence(state)}
    return state

def decision_node(state: ProcurementState) -> dict:
    from agents.decision.risk_scoring import run_risk_scoring
    from agents.decision.negotiation_strategy import run_negotiation_strategy

    # Step 1 — Risk scoring
    result = run_risk_scoring(state)
    state = {**state, **result}

    # Step 2 — Negotiation strategy
    neg_result = run_negotiation_strategy(state)
    state = {**state, **neg_result}

    log = list(state.get("audit_log", []))

    # Step 3 — Final decision
    risk_flag = state.get("risk_flag", False)
    trend = state.get("price_forecast", {}).get("trend", "stable")

    if risk_flag:
        decision = "escalate"
        log.append(f"[{datetime.now().isoformat()}] Decision: ESCALATE — all suppliers risky")
    elif trend == "falling":
        decision = "wait"
        log.append(f"[{datetime.now().isoformat()}] Decision: WAIT — prices are falling")
    else:
        decision = "buy"
        log.append(f"[{datetime.now().isoformat()}] Decision: BUY — safe supplier, prices stable or rising")

    return {
        **state,
        "decision": decision,
        "audit_log": log
    }


def human_gate_node(state: ProcurementState) -> dict:
    log = list(state.get("audit_log", []))
    log.append(f"[{datetime.now().isoformat()}] Human approved. Proceeding to documents.")
    return {"audit_log": log}


def document_node(state: ProcurementState) -> dict:
    from agents.document.rfq_generator import run_rfq_generator
    from agents.document.contract_drafter import run_contract_drafter
    from intelligence.spend_analytics import build_spend_record, summarize_spend
    from intelligence.supplier_scorecard import update_scorecard, get_top_suppliers
    import uuid

    # Step 1 — RFQ
    rfq_result = run_rfq_generator(state)
    state = {**state, **rfq_result}

    # Step 2 — Contract
    contract_result = run_contract_drafter(state)
    state = {**state, **contract_result}

    # Step 3 — PO number
    log = list(state.get("audit_log", []))
    po = f"PO-{uuid.uuid4().hex[:8].upper()}"
    log.append(f"[{datetime.now().isoformat()}] Purchase Order generated: {po}")

    # Step 4 — Intelligence layer
    spend_record = build_spend_record({**state, "po_number": po})
    log.append(
        f"[{datetime.now().isoformat()}] "
        f"Spend recorded: ₹{spend_record['total_spend']:,.0f} | "
        f"Savings: ₹{spend_record['total_savings']:,.0f} ({spend_record['savings_pct']}%)"
    )

    log.append(f"[{datetime.now().isoformat()}] Workflow complete — all documents ready")

    return {
        **state,
        "po_number": po,
        "completed_at": datetime.now().isoformat(),
        "audit_log": log
    }


def route_after_decision(state: ProcurementState) -> str:
    if state.get("decision") == "escalate":
        return END
    return "human_gate"


# ── Checkpointer ──────────────────────────────────────────────────────────────
# Locally: always MemorySaver (no Redis Stack needed)
# On Railway: set USE_REDIS_SAVER=true in dashboard to switch to RedisSaver
# ─────────────────────────────────────────────────────────────────────────────

REDIS_URL = os.getenv("REDIS_URL")
USE_REDIS_SAVER = os.getenv("USE_REDIS_SAVER", "false").lower() == "true"

if REDIS_URL and USE_REDIS_SAVER:
    from langgraph.checkpoint.redis import RedisSaver
    checkpointer = RedisSaver(REDIS_URL)
    print("✓ Using RedisSaver for checkpointing")
else:
    checkpointer = MemorySaver()
    print("✓ Using MemorySaver for checkpointing (local dev)")


def build_graph():
    builder = StateGraph(ProcurementState)

    builder.add_node("research", research_node)
    builder.add_node("decision", decision_node)
    builder.add_node("human_gate", human_gate_node)
    builder.add_node("document", document_node)

    builder.set_entry_point("research")
    builder.add_edge("research", "decision")
    builder.add_conditional_edges("decision", route_after_decision)
    builder.add_edge("human_gate", "document")
    builder.add_edge("document", END)

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_gate"]
    )


graph = build_graph()