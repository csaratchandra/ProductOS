# ProductOS Finance Domain Pack

**Version:** 1.0.0  
**Status:** Draft  
**Last Updated:** 2026-05-13

Cross-regional finance intelligence for ProductOS V14.

## Structure

- `base.schema.overlay.json` — ISO 20022, LEI, risk terminology, audit patterns
- `regions/us.schema.overlay.json` — SEC, FINRA, CFTC, OCC, Federal Reserve
- `regions/eu.schema.overlay.json` — MiFID II, EMIR, ECB, EBA
- `workflows/trade_execution.workflow.json` — FIX protocol, order management
- `sub-packs/capital_markets.manifest.json` — FIX, OMS, derivatives, clearing
- `sub-packs/banking.manifest.json` — PCI-DSS, SWIFT, AML/KYC, lending
