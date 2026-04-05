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


def run_rfq_generator(state: ProcurementState) -> dict:
    log = list(state.get("audit_log", []))
    supplier = state.get("selected_supplier")
    item = state.get("item", "")
    quantity = state.get("quantity", 0)
    budget = state.get("budget", 0.0)
    deadline = state.get("deadline", "")
    market_avg = state.get("market_price_avg", 0.0)
    request_id = state.get("request_id", "")

    log.append(f"[{datetime.now().isoformat()}] RFQ Generator started")

    supplier_name = supplier["name"] if supplier else "Vendor"
    supplier_price = supplier["price"] if supplier else 0.0

    prompt = f"""You are a professional procurement officer. Write a formal Request For Quotation (RFQ) document.

DETAILS:
- RFQ Reference: RFQ-{request_id[:8].upper()}
- Date: {datetime.now().strftime("%d %B %Y")}
- To: {supplier_name}
- Item: {item}
- Quantity: {quantity} units
- Target price per unit: {round(market_avg * 0.95, 2)} (5% below market average of {market_avg})
- Maximum budget per unit: {round(budget / quantity if quantity > 0 else budget, 2)}
- Required delivery by: {deadline}

Write a professional RFQ with these sections:
1. Header (RFQ reference, date, to/from)
2. Scope of Supply (what we need)
3. Quantity and Specifications
4. Pricing Requirements (target price, payment terms)
5. Delivery Requirements
6. Terms and Conditions (3 standard clauses)
7. Response Deadline (set to 7 days from today)
8. Contact Information (use placeholder)

Keep it professional, concise, and under 300 words."""

    response = llm.invoke(prompt)
    rfq_text = response.content.strip()

    log.append(f"[{datetime.now().isoformat()}] RFQ generated for {supplier_name}")
    log.append(f"[{datetime.now().isoformat()}] RFQ reference: RFQ-{request_id[:8].upper()}")

    return {
        "rfq_text": rfq_text,
        "audit_log": log
    }