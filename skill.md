# Skill: Arc Agent Payment Boundary

## What it does

Provides a pre/post-payment safety boundary for AI agents performing USDC transfers on Arc Testnet.

- **Pre-payment check**: Validates budget limits, risk level, and approval requirements before a payment is attempted
- **Post-payment record**: Stores the Arc Testnet tx hash and ArcScan URL for audit trail after an external payment execution
- **Audit report**: Returns payment history, amounts, and audit readiness for a given agent

Use this when:
- an AI agent is about to make or approve a payment
- a developer needs to separate approval from execution
- a reviewer needs payment evidence before or after execution
- a system needs a boundary between agent intent and wallet execution

Do not use this as:
- an official Arc service
- an official Circle service
- a production payment gateway
- a wallet
- a settlement layer

## When to use

- An AI agent is about to execute a USDC transfer on Arc Testnet and needs budget/risk validation first
- A tx hash from an Arc Testnet payment is available and needs to be logged for audit purposes
- A human or AI auditor needs to review payment records for a specific agent

## When NOT to use

- To execute, sign, or submit blockchain transactions (this skill does not do that)
- To manage, store, or transmit private keys or seed phrases
- For production payment custody or financial management
- For legal, tax, or regulatory compliance decisions
- As a substitute for production-grade audit infrastructure

## Inputs

### POST /api/arc/payment/check
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| agent_id | string | yes | Identifier for the AI agent |
| payer_wallet | string | yes | Testnet wallet address of payer |
| payee_wallet | string | yes | Testnet wallet address of payee |
| amount_usdc | float | yes | Amount in USDC |
| payment_purpose | string | yes | Description of payment purpose |
| requested_tool | string | yes | Tool requesting the payment |
| risk_context | string | no | Risk flags (e.g. "normal", "high_risk") |
| per_payment_limit | float | no | Max USDC per payment (default: 10.0) |
| daily_limit | float | no | Max USDC per day (default: 100.0) |
| requires_human_approval_threshold | float | no | Threshold for human approval (default: 5.0) |

### POST /api/arc/payment/record
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| agent_id | string | yes | Identifier for the AI agent |
| check_result_id | string | yes | ID from previous /check call |
| tx_hash | string | no | Arc Testnet transaction hash |
| arcscan_url | string | no | ArcScan URL for tx verification |
| amount_usdc | float | yes | Amount recorded |
| payee_wallet | string | yes | Payee wallet address |
| payment_purpose | string | yes | Description of payment purpose |
| payment_status | string | yes | One of: success, confirmed, completed, failed |

## Outputs

### From /check
- `payment_check_status`: approved / denied / requires_review
- `allowed`: boolean
- `requires_human_approval`: boolean
- `risk_level`: low / high
- `budget_status`: within_limit / over_limit
- `recommended_next_step`: next action to take
- `check_result_id`: ID to use in subsequent /record call

### From /record
- `record_status`: recorded
- `audit_ready`: true if payment_status is success / confirmed / completed
- `record_id`: unique record identifier
- `recommended_next_step`: audit_log_complete or update_status_when_tx_confirmed

### From /report/{agent_id}
- `total_payments`: count of recorded payments
- `total_amount_usdc`: sum of recorded amounts
- `payment_records`: list with tx_hash, arcscan_url, amount, status, timestamp
- `audit_ready_count`: count of audit-ready records

## Example flow

```
1. POST /api/arc/payment/check
   → payment_check_status: approved
   → check_result_id: chk_abc123

2. [External] User/wallet executes Arc Testnet USDC payment
   → tx_hash: 0x750db7...59f1

3. POST /api/arc/payment/record
   → check_result_id: chk_abc123
   → tx_hash: 0x750db7...59f1
   → payment_status: success
   → audit_ready: true

4. GET /api/arc/payment/report/arc_agent_001
   → total_payments: 1
   → audit_ready_count: 1
   → payment_records[0].tx_hash: 0x750db7...59f1
```

## Constraints

- This skill does NOT execute payments, sign transactions, or interact with wallets
- Does NOT handle private keys or seed phrases
- Does NOT provide custody or fund management
- Local JSON storage is ephemeral (demo environment) — not production audit storage
- Arc Testnet only (Chain ID: 5042002)
- Not affiliated with Circle or Arc

## Safety notes

- Always use testnet wallet addresses only
- Never pass private keys or seed phrases to any endpoint
- The `check` result does not guarantee payment success — it only validates budget and risk constraints
- `audit_ready: true` means the record is logged, not that the payment is legally audited
- Render storage is ephemeral — do not rely on it for permanent records
