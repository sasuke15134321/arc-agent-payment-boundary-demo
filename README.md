# Arc Agent Payment Boundary Demo

Minimum Payment Boundary API skeleton for AI agent USDC payments on Arc Testnet.

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
