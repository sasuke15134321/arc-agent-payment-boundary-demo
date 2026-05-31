import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Storage paths
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
CHECKS_FILE = DATA_DIR / "payment_checks.json"
RECORDS_FILE = DATA_DIR / "payment_records.json"

DATA_DIR.mkdir(exist_ok=True)


def _load_json(path: Path) -> list:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class PaymentCheckRequest(BaseModel):
    agent_id: str
    payer_wallet: str
    payee_wallet: str
    amount_usdc: float
    payment_purpose: str
    requested_tool: str
    risk_context: str = ""
    per_payment_limit: float = 10.0
    daily_limit: float = 100.0
    requires_human_approval_threshold: float = 5.0


class PaymentCheckResponse(BaseModel):
    payment_check_status: str
    allowed: bool
    requires_human_approval: bool
    risk_level: str
    budget_status: str
    recommended_next_step: str
    check_result_id: str


class PaymentRecordRequest(BaseModel):
    agent_id: str
    check_result_id: str
    tx_hash: str = ""
    arcscan_url: str = ""
    amount_usdc: float
    payee_wallet: str
    payment_purpose: str
    payment_status: str


class PaymentRecordResponse(BaseModel):
    record_status: str
    audit_ready: bool
    record_id: str
    recommended_next_step: str


class PaymentRecordItem(BaseModel):
    record_id: str
    check_result_id: str
    tx_hash: str
    arcscan_url: str
    amount_usdc: float
    payee_wallet: str
    payment_purpose: str
    payment_status: str
    recorded_at: str


class ReportResponse(BaseModel):
    agent_id: str
    total_payments: int
    total_amount_usdc: float
    payment_records: List[PaymentRecordItem]
    human_review_required_count: int
    audit_ready_count: int


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Arc Agent Payment Boundary Demo",
    version="0.1.0",
    description=(
        "Minimum Payment Boundary demo API for AI agents on Arc Testnet. "
        "Step 1: check / record / report with local JSON storage. "
        "No private keys, no mainnet, no real funds."
    ),
)

_HIGH_RISK_KEYWORDS = {"suspicious", "unknown", "high_risk"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "arc_testnet": {
            "rpc_url": "https://rpc.testnet.arc.network",
            "chain_id": 5042002,
            "explorer": "https://testnet.arcscan.app",
        },
        "note": "Testnet demo only. No real funds.",
    }


@app.post("/api/arc/payment/check", response_model=PaymentCheckResponse)
def payment_check(req: PaymentCheckRequest):
    check_result_id = f"chk_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.utcnow().isoformat() + "Z"

    # ---- Risk level ----
    risk_words = {w.lower() for w in req.risk_context.replace(",", " ").split()}
    risk_level = "high" if risk_words & _HIGH_RISK_KEYWORDS else "low"

    # ---- Budget status ----
    budget_status = (
        "within_limit" if req.amount_usdc <= req.per_payment_limit else "over_limit"
    )

    # ---- Decision logic ----
    if req.amount_usdc > req.per_payment_limit:
        status = "denied"
        allowed = False
        requires_human_approval = False
        next_step = "reduce_amount_below_per_payment_limit"
    elif risk_level == "high" or req.amount_usdc >= req.requires_human_approval_threshold:
        status = "requires_review"
        allowed = False
        requires_human_approval = True
        next_step = "request_human_approval_before_payment"
    else:
        status = "approved"
        allowed = True
        requires_human_approval = False
        next_step = "proceed_to_payment_record_after_tx"

    # ---- Persist check (no secrets stored) ----
    checks = _load_json(CHECKS_FILE)
    checks.append({
        "check_result_id": check_result_id,
        "agent_id": req.agent_id,
        "payer_wallet": req.payer_wallet,
        "payee_wallet": req.payee_wallet,
        "amount_usdc": req.amount_usdc,
        "payment_purpose": req.payment_purpose,
        "requested_tool": req.requested_tool,
        "payment_check_status": status,
        "allowed": allowed,
        "requires_human_approval": requires_human_approval,
        "risk_level": risk_level,
        "budget_status": budget_status,
        "checked_at": timestamp,
    })
    _save_json(CHECKS_FILE, checks)

    return PaymentCheckResponse(
        payment_check_status=status,
        allowed=allowed,
        requires_human_approval=requires_human_approval,
        risk_level=risk_level,
        budget_status=budget_status,
        recommended_next_step=next_step,
        check_result_id=check_result_id,
    )


@app.post("/api/arc/payment/record", response_model=PaymentRecordResponse)
def payment_record(req: PaymentRecordRequest):
    record_id = f"rec_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.utcnow().isoformat() + "Z"

    normalized_status = req.payment_status.lower()
    audit_ready = normalized_status in ("success", "confirmed", "completed")

    records = _load_json(RECORDS_FILE)
    records.append({
        "record_id": record_id,
        "agent_id": req.agent_id,
        "check_result_id": req.check_result_id,
        "tx_hash": req.tx_hash,
        "arcscan_url": req.arcscan_url,
        "amount_usdc": req.amount_usdc,
        "payee_wallet": req.payee_wallet,
        "payment_purpose": req.payment_purpose,
        "payment_status": req.payment_status,
        "audit_ready": audit_ready,
        "recorded_at": timestamp,
    })
    _save_json(RECORDS_FILE, records)

    return PaymentRecordResponse(
        record_status="recorded",
        audit_ready=audit_ready,
        record_id=record_id,
        recommended_next_step=(
            "audit_log_complete" if audit_ready else "update_status_when_tx_confirmed"
        ),
    )


@app.get("/api/arc/payment/report/{agent_id}", response_model=ReportResponse)
def payment_report(agent_id: str):
    records = [r for r in _load_json(RECORDS_FILE) if r.get("agent_id") == agent_id]
    checks = _load_json(CHECKS_FILE)
    human_review_count = sum(
        1 for c in checks
        if c.get("agent_id") == agent_id and c.get("requires_human_approval")
    )
    audit_ready_count = sum(1 for r in records if r.get("audit_ready"))

    return ReportResponse(
        agent_id=agent_id,
        total_payments=len(records),
        total_amount_usdc=round(sum(r.get("amount_usdc", 0) for r in records), 6),
        payment_records=[PaymentRecordItem(**r) for r in records],
        human_review_required_count=human_review_count,
        audit_ready_count=audit_ready_count,
    )
