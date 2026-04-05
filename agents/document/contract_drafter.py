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


def run_contract_drafter(state: ProcurementState) -> dict:
    log = list(state.get("audit_log", []))
    supplier = state.get("selected_supplier")
    item = state.get("item", "")
    quantity = state.get("quantity", 0)
    budget = state.get("budget", 0.0)
    deadline = state.get("deadline", "")
    request_id = state.get("request_id", "")
    negotiation_strategy = state.get("negotiation_strategy", "")

    log.append(f"[{datetime.now().isoformat()}] Contract Drafter started")

    supplier_name = supplier["name"] if supplier else "Vendor"
    supplier_price = supplier["price"] if supplier else 0.0
    total_value = supplier_price * quantity

    prompt = f"""You are a procurement legal specialist. Draft a purchase contract.

CONTRACT DETAILS:
- Contract Reference: CON-{request_id[:8].upper()}
- Date: {datetime.now().strftime("%d %B %Y")}
- Buyer: ProcureIQ Client Company
- Seller: {supplier_name}
- Item: {item}
- Quantity: {quantity} units
- Agreed price per unit: {supplier_price}
- Total contract value: {total_value}
- Delivery deadline: {deadline}

NEGOTIATION CONTEXT:
{negotiation_strategy[:300] if negotiation_strategy else "Standard terms apply"}

Draft a professional purchase contract with these clauses:
1. Parties (buyer and seller details)
2. Scope of Supply
3. Price and Payment Terms (30% advance, 70% on delivery)
4. Delivery Terms (location, timeline, penalties for delay)
5. Quality and Inspection Rights
6. Warranty (minimum 12 months)
7. Liability and Indemnification
8. Termination Clause
9. Governing Law
10. Signatures section

Keep it under 400 words. Professional legal style."""

    response = llm.invoke(prompt)
    contract_text = response.content.strip()

    log.append(f"[{datetime.now().isoformat()}] Contract drafted for {supplier_name}")
    log.append(f"[{datetime.now().isoformat()}] Contract reference: CON-{request_id[:8].upper()}")
    log.append(f"[{datetime.now().isoformat()}] Total contract value: {total_value}")

    return {
        "contract_text": contract_text,
        "audit_log": log
    }