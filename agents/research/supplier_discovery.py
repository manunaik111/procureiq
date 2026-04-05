from langchain_groq import ChatGroq
from duckduckgo_search import DDGS
from orchestrator.state import ProcurementState, SupplierInfo
from datetime import datetime
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def search_suppliers(item: str, quantity: int) -> list[dict]:
    """Search DuckDuckGo for real vendors."""
    queries = [
        f"{item} supplier India wholesale price",
        f"buy {item} bulk vendor manufacturer",
        f"{item} distributor price per unit"
    ]

    results = []
    with DDGS() as ddgs:
        for query in queries:
            try:
                hits = list(ddgs.text(query, max_results=3))
                results.extend(hits)
            except Exception as e:
                print(f"Search failed for query '{query}': {e}")
                continue

    return results[:8]


def extract_suppliers_with_llm(
    item: str,
    quantity: int,
    budget: float,
    search_results: list[dict]
) -> list[SupplierInfo]:
    """Use Groq to extract structured supplier data from search results."""

    results_text = ""
    for i, r in enumerate(search_results):
        results_text += f"\nResult {i+1}:\nTitle: {r.get('title', '')}\nURL: {r.get('href', '')}\nSummary: {r.get('body', '')}\n"

    prompt = f"""You are a procurement analyst. A company needs to buy {quantity} units of "{item}" with a budget of {budget}.

Here are web search results about potential suppliers:
{results_text}

Extract up to 5 real suppliers from these results. For each supplier return a JSON array with this exact format:
[
  {{
    "name": "Supplier company name",
    "url": "their website URL",
    "price": estimated price per unit as a number (make a reasonable estimate if not stated),
    "risk_score": a risk score from 0.0 (very safe) to 1.0 (very risky) based on how established they seem,
    "notes": "one sentence about why this supplier looks good or concerning"
  }}
]

Return ONLY the JSON array. No explanation. No markdown. Just the raw JSON array."""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    # Clean up response in case Groq adds any markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        suppliers = json.loads(raw)
        validated = []
        for s in suppliers:
            validated.append(SupplierInfo(
                name=str(s.get("name", "Unknown")),
                url=str(s.get("url", "")),
                price=float(s.get("price", 0.0)),
                risk_score=float(s.get("risk_score", 0.5)),
                notes=str(s.get("notes", ""))
            ))
        return validated
    except Exception as e:
        return [SupplierInfo(
            name="Manual Review Required",
            url="",
            price=0.0,
            risk_score=0.8,
            notes=f"LLM parsing failed: {str(e)}"
        )]


def calculate_market_average(suppliers: list[SupplierInfo]) -> float:
    """Calculate average price across all found suppliers."""
    prices = [s["price"] for s in suppliers if s["price"] > 0]
    if not prices:
        return 0.0
    return round(sum(prices) / len(prices), 2)


def run_supplier_discovery(state: ProcurementState) -> dict:
    """Main function called by the LangGraph research node."""
    log = list(state.get("audit_log", []))
    item = state["item"]
    quantity = state["quantity"]
    budget = state["budget"]

    log.append(f"[{datetime.now().isoformat()}] Supplier Discovery started for: {item} x{quantity}")

    # Step 1: Search the web
    log.append(f"[{datetime.now().isoformat()}] Searching web for suppliers...")
    search_results = search_suppliers(item, quantity)
    log.append(f"[{datetime.now().isoformat()}] Found {len(search_results)} search results")

    # Step 2: Extract structured data with Groq
    log.append(f"[{datetime.now().isoformat()}] Extracting supplier data with Groq LLM...")
    suppliers = extract_suppliers_with_llm(item, quantity, budget, search_results)
    log.append(f"[{datetime.now().isoformat()}] Extracted {len(suppliers)} suppliers")

    # Step 3: Calculate market average
    market_avg = calculate_market_average(suppliers)
    log.append(f"[{datetime.now().isoformat()}] Market average price: {market_avg} per unit")

    # Log each supplier found
    for s in suppliers:
        log.append(f"[{datetime.now().isoformat()}] Supplier found: {s['name']} | Price: {s['price']} | Risk: {s['risk_score']}")

    # Fix 10: Honesty disclaimer
    log.append(f"[{datetime.now().isoformat()}] NOTE: Suppliers are AI-extracted candidates from web search. Manual verification recommended before contract signing.")

    return {
        "suppliers": suppliers,
        "market_price_avg": market_avg,
        "audit_log": log,
    }