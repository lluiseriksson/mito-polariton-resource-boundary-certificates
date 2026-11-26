# MITO-POLARITON-BOUND-CERT-1.0

Exact Hopfield $A^2$ polariton invariants, bioenergetic resource-horizon bounds, and constructive Lean 4.35.0 verification suite uniting Lluis Eriksson's operational coherence-maintenance program (`ARR-2025-2AQXS44H6Z8GQAG2` and companion AIRR.SCIENCE records) with the 71.0-THz mitochondrial cristae mito-polariton model of Yang, Gu, and Song (`bioRxiv:10.64898/2026.09.10.750628v1`, September 2026).

## Reproduction
```bash
(cd lean && lake build)
python -m src.mito_polariton_bound_verifier certificates
pytest -q
```

## Licenses
- Code, Lean 4 proofs, scripts, and certificates: **MIT** (`LICENSE-CODE`)
- Manuscript and figures: **CC-BY-4.0** (`LICENSE-DOCS`)
