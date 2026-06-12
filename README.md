# Arc Agent Payment Boundary Demo

AI-agent payment boundary demo on Arc Testnet.

Use this demo when an AI agent needs to decide whether a payment should be approved before execution.

It helps separate:
- payment intent
- approval decision
- execution boundary
- payment evidence
- human review

This is useful for agents, developers, and reviewers who need a small external control layer around AI-agent payments.

Independent Arc Testnet demo.
Not official Arc or Circle.
Does not execute payments.
Testnet only.
Not a production payment gateway.

## Step 1 scope

- `POST /api/arc/payment/check` — pre-payment check (budget / risk / human approval)
- `POST /api/arc/payment/record` — post-payment record (tx_hash / amount / purpose)
- `GET /api/arc/payment/report/{agent_id}` — payment report / audit log
- `GET /health` — health check

Storage: local JSON (`data/payment_checks.json`, `data/payment_records.json`).

## Arc Testnet settings (confirmed)

| Item | Value |
|------|-------|
| RPC URL | https://rpc.testnet.arc.network |
| Chain ID | 5042002 |
| Explorer | https://testnet.arcscan.app |

## Quick start

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open: http://localhost:8000/docs

## NOT in Step 1

- No Arc transaction execution
- No private key / seed phrase handling
- No wallet signing
- No mainnet connection
- No real funds

## Security

`data/*.json` stores only: wallet address, tx hash, amount, purpose, timestamp.
No private keys, no seed phrases are ever saved.

## Render deploy / demo notes

- **Arc Testnet demo only** — not connected to Arc Mainnet
- **Does not execute payments** — no transaction signing or submission
- **Does not custody funds** — no wallet, no private key handling
- **Does not handle private keys or seed phrases**
- **Local JSON storage is demo-only** — not production audit storage; data is ephemeral on Render free tier
- Chain ID: 5042002
- RPC: https://rpc.testnet.arc.network
- Explorer: https://testnet.arcscan.app

Render Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

This project is an independent demo and is not officially affiliated with Circle, Arc, or any related organizations.

## AI-readable files

- [openapi.yaml](openapi.yaml) — OpenAPI 3.1.0 schema for all endpoints
- [llms.txt](llms.txt) — AI agent guidance: when to use, call flow, constraints
- [skill.md](skill.md) — Skill description for Claude / AI agents
- [/.well-known/agent.json](.well-known/agent.json) — Agent manifest for AI agent discovery
