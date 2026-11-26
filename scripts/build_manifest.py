"""Build deterministic SHA-256 manifest for MITO-POLARITON-BOUND-CERT-1.0."""

from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"

INCLUDE_PATTERNS = [
    "README.md",
    "LICENSE-CODE",
    "LICENSE-DOCS",
    "lean/lean-toolchain",
    "lean/lakefile.toml",
    "lean/MitoPolaritonBoundCert.lean",
    "src/__init__.py",
    "src/mito_polariton_bound_verifier.py",
    "scripts/generate_certificates.py",
    "scripts/generate_figures.py",
    "scripts/build_manifest.py",
    "tests/test_verifier.py",
    "paper/main.tex",
    "paper/references.bib",
    "paper/main.pdf",
]


def main() -> int:
    paths: list[pathlib.Path] = []
    for rel in INCLUDE_PATTERNS:
        p = ROOT / rel
        if p.is_file():
            paths.append(p)
    for sub in ("certificates", "paper/figures"):
        d = ROOT / sub
        if d.is_dir():
            paths.extend(sorted(x for x in d.iterdir() if x.is_file()))
    lines = []
    for p in sorted(set(paths), key=lambda x: x.relative_to(ROOT).as_posix()):
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{digest}  {p.relative_to(ROOT).as_posix()}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote MANIFEST.sha256 with {len(lines)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
