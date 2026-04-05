from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field, validator
from orchestrator.graph import graph
from orchestrator.state import ProcurementState
from data.models import init_db
from datetime import datetime, timedelta
from typing import Optional
import uuid
import os
import asyncio
import logging

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ProcureIQ", version="0.1.0")


@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database tables initialized.")


# ── Auth ──────────────────────────────────────────────────
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ── Request model with validation ─────────────────────────
class ProcurementRequest(BaseModel):
    item: str = Field(..., min_length=3, max_length=200)
    quantity: int = Field(..., gt=0, le=100000)
    budget: float = Field(..., gt=0)
    deadline: str = Field(..., min_length=8)

    @validator("deadline")
    def deadline_must_be_future(cls, v):
        try:
            d = datetime.strptime(v, "%Y-%m-%d")
            if d <= datetime.now():
                raise ValueError("Deadline must be in the future")
        except ValueError as e:
            raise ValueError(f"Invalid deadline: {e}")
        return v

    @validator("item")
    def item_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Item cannot be blank")
        return v.strip()


# ── Endpoints ──────────────────────────────────────────────
@app.post("/procure", dependencies=[Depends(verify_api_key)])
async def start_procurement(req: ProcurementRequest):
    try:
        request_id = str(uuid.uuid4())
        logger.info(f"[{request_id}] Procurement request started for: {req.item}")

        initial_state: ProcurementState = {
            "request_id": request_id,
            "item": req.item,
            "quantity": req.quantity,
            "budget": req.budget,
            "deadline": req.deadline,
            "suppliers": [],
            "market_price_avg": 0.0,
            "price_forecast": {},
            "selected_supplier": None,
            "risk_flag": False,
            "negotiation_strategy": "",
            "decision": "",
            "human_approved": False,
            "approver_notes": "",
            "rfq_text": "",
            "contract_text": "",
            "po_number": "",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "audit_log": [],
        }

        config = {"configurable": {"thread_id": request_id}}
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, lambda: graph.invoke(initial_state, config=config)
            ),
            timeout=120.0
        )

        # ── Send approval email ──
        try:
            from integrations.email_notify import send_approval_email
            # Merge initial state with agent results for full context
            full_state = {**initial_state, **result}
            email_sent = send_approval_email(full_state)
            if email_sent:
                logger.info(f"[{request_id}] Approval email sent")
            else:
                logger.warning(f"[{request_id}] Email not sent - check credentials")
        except Exception as email_err:
            logger.warning(f"[{request_id}] Email failed: {email_err}")

        logger.info(f"[{request_id}] Awaiting human approval")
        return {
            "request_id": request_id,
            "status": "awaiting_approval",
            "disclaimer": "Suppliers are web-search candidates extracted by AI. Verify before committing.",
            "audit_log": result["audit_log"],
        }

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Workflow timed out after 120 seconds")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/approve/{request_id}", dependencies=[Depends(verify_api_key)])
async def approve_procurement(request_id: str, notes: str = ""):
    try:
        config = {"configurable": {"thread_id": request_id}}
        graph.update_state(
            config,
            {"human_approved": True, "approver_notes": notes}
        )
        logger.info(f"[{request_id}] Approval received. Resuming workflow.")
        result = graph.invoke(None, config=config)

        # ── Save to database ──
        from data.db_ops import save_procurement
        full_state = graph.get_state(config)
        if full_state and full_state.values:
            save_procurement(full_state.values)

        logger.info(f"[{request_id}] Workflow completed. PO: {result.get('po_number')}")
        return {
            "request_id": request_id,
            "status": "completed",
            "po_number": result.get("po_number"),
            "rfq_reference": f"RFQ-{request_id[:8].upper()}",
            "contract_reference": f"CON-{request_id[:8].upper()}",
            "audit_log": result.get("audit_log"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{request_id}")
async def get_status(request_id: str):
    try:
        config = {"configurable": {"thread_id": request_id}}
        state = graph.get_state(config)
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Request not found")
        values = state.values
        return {
            "request_id": request_id,
            "item": values.get("item"),
            "decision": values.get("decision"),
            "selected_supplier": values.get("selected_supplier"),
            "po_number": values.get("po_number"),
            "human_approved": values.get("human_approved"),
            "completed_at": values.get("completed_at"),
            "audit_log": values.get("audit_log"),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Request not found")


@app.get("/health")
async def health():
    return {"status": "ok"}
