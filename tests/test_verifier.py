"""Unit, forgery, AST zero-float, and exact algebraic tests for MITO-POLARITON-BOUND-CERT-1.0."""

from __future__ import annotations

import ast
import copy
import json
import pathlib
import sys
from fractions import Fraction

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import mito_polariton_bound_verifier as V

CERTS_DIR = ROOT / "certificates"


def _load(name: str) -> dict:
    return json.loads((CERTS_DIR / name).read_text(encoding="utf-8"))


def test_ast_zero_float_and_no_forbidden_imports() -> None:
    src_path = ROOT / "src" / "mito_polariton_bound_verifier.py"
    tree = ast.parse(src_path.read_text(encoding="utf-8"), filename=str(src_path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            pytest.fail(f"Forbidden float literal {node.value!r} at line {node.lineno}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float":
            pytest.fail(f"Forbidden float() call at line {node.lineno}")
        if isinstance(node, ast.Div):
            pytest.fail(f"Forbidden true-division operator / at line {node.lineno}")
        if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Div):
            pytest.fail(f"Forbidden true-division /= at line {node.lineno}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in {"math", "numpy", "scipy", "decimal"}
        if isinstance(node, ast.ImportFrom):
            assert node.module not in {"math", "numpy", "scipy", "decimal"}


@pytest.mark.parametrize("cert_path", sorted(CERTS_DIR.glob("*.json")), ids=lambda p: p.name)
def test_all_16_canonical_certificates_pass(cert_path: pathlib.Path) -> None:
    res = V.verify_file(cert_path)
    assert res["schema_version"] == V.SCHEMA_VERSION
    assert res["cert_id"].startswith("C")


def test_key_exact_physics_and_horizon_metrics() -> None:
    r01 = V.verify_file(CERTS_DIR / "C01_mito_71_87_hopfield_trk_shift.json")
    assert r01["nu_plus_rwa_thz"] == [103, 1]
    assert r01["nu_plus_hopfield_thz"] == [7569, 71]
    assert r01["asymmetric_shift_thz"] == [256, 71]
    assert r01["eta_hopfield"] == [1264, 6177]
    assert r01["is_ultrastrong_gt_0p1"] is True

    r05 = V.verify_file(CERTS_DIR / "C05_regime1_passive_equilibrium_zero_cost.json")
    assert r05["feasible_under_atp_budget"] is True
    assert r05["regime"] == "Regime_I_Passive_Equilibrium"

    r06 = V.verify_file(CERTS_DIR / "C06_horizon_violation_bulk_water_dephasing.json")
    assert r06["feasible_under_atp_budget"] is False
    assert r06["regime"] == "Horizon_Violation_Infeasible"

    r09 = V.verify_file(CERTS_DIR / "C09_omega0_dirichlet_floor_active.json")
    assert r09["dirichlet_omega0_rate"] == [2000000, 1]
    assert r09["has_irreducible_floor"] is True

    r11 = V.verify_file(CERTS_DIR / "C11_cristae_collar_rip_u_with_floor.json")
    assert r11["lorentzian_suppression_factor"] == [5, 1]

    r13 = V.verify_file(CERTS_DIR / "C13_bosonic_dark_mode_leakage_71thz_10e6.json")
    assert Fraction(*r13["hopfield_matter_weight"]) == Fraction(7569, 12610)
    assert Fraction(*r13["hopfield_photonic_weight"]) == Fraction(5041, 12610)
    assert Fraction(*r13["thermal_occ_certified_ub"]) < Fraction(1, 500000)


# Adversarial forgery tests
def test_reject_float_and_dup_json(tmp_path: pathlib.Path) -> None:
    p1 = tmp_path / "f.json"
    p1.write_text('{"x": 71.0}', encoding="utf-8")
    with pytest.raises(V.VerificationError, match="floating-point"):
        V.verify_file(p1)
    p2 = tmp_path / "d.json"
    p2.write_text('{"a": 1, "a": 2}', encoding="utf-8")
    with pytest.raises(V.VerificationError, match="Duplicate"):
        V.verify_file(p2)


def test_reject_non_reduced_rational() -> None:
    c = _load("C01_mito_71_87_hopfield_trk_shift.json")
    c["payload"]["omega_0_thz"] = [174, 2]
    with pytest.raises(V.VerificationError, match="lowest terms"):
        V.verify_certificate(c)


def test_reject_false_rwa_claimed_as_hopfield() -> None:
    c = _load("C01_mito_71_87_hopfield_trk_shift.json")
    c["payload"]["expected_nu_plus_hop"] = [103, 1]
    with pytest.raises(V.VerificationError, match="nu_plus_hop mismatch"):
        V.verify_certificate(c)


def test_reject_false_feasibility_claim_for_bulk_water() -> None:
    c = _load("C06_horizon_violation_bulk_water_dephasing.json")
    c["payload"]["expected_feasible"] = True
    with pytest.raises(V.VerificationError, match="Feasibility mismatch"):
        V.verify_certificate(c)


def test_reject_mismatched_temperature_and_kbt() -> None:
    c = _load("C06_horizon_violation_bulk_water_dephasing.json")
    c["payload"]["temperature_K"] = [400, 1]  # inconsistent with kBT_meV = 26.71
    with pytest.raises(V.VerificationError, match="inconsistent with SI-2019"):
        V.verify_certificate(c)


def test_reject_non_bool_expected_feasible() -> None:
    c = _load("C06_horizon_violation_bulk_water_dephasing.json")
    c["payload"]["expected_feasible"] = "false"
    with pytest.raises(V.VerificationError, match="boolean"):
        V.verify_certificate(c)


def test_reject_invalid_isotope_bracket() -> None:
    c = _load("C03_cd2_deuterated_lipid_polariton.json")
    c["payload"]["nu_minus_lo_thz"] = [60, 1]
    c["payload"]["nu_minus_hi_thz"] = [61, 1]
    with pytest.raises(V.VerificationError, match="Lower bracket"):
        V.verify_certificate(c)


def test_reject_non_normalized_sigma_in_mode3() -> None:
    c = _load("C09_omega0_dirichlet_floor_active.json")
    c["payload"]["sigma_plus"] = [1, 4]
    with pytest.raises(V.VerificationError, match="stationary distribution"):
        V.verify_certificate(c)


def test_reject_non_increasing_collar_steps() -> None:
    c = _load("C11_cristae_collar_rip_u_with_floor.json")
    c["payload"]["collar_steps"] = [2, 2, 4]
    with pytest.raises(V.VerificationError, match="strictly increasing"):
        V.verify_certificate(c)


def test_reject_false_thermal_occupation_bound() -> None:
    c = _load("C13_bosonic_dark_mode_leakage_71thz_10e6.json")
    c["payload"]["thermal_occ_upper_bound"] = [1, 10000000]  # 1e-7 < true ~1.41e-6!
    with pytest.raises(V.VerificationError, match="Thermal occupation bound"):
        V.verify_certificate(c)


def test_reject_no_passive_network_separation() -> None:
    c = _load("C15_passive_network_S5_irreducible_gap.json")
    c["payload"]["irreducible_stopband_leak"] = [4, 5]  # exceeds 1 - 12*(2/100) = 0.76
    with pytest.raises(V.VerificationError, match="No strict separation"):
        V.verify_certificate(c)


def test_reject_schema_mode_and_file_guards(tmp_path: pathlib.Path) -> None:
    bad = copy.deepcopy(_load("C01_mito_71_87_hopfield_trk_shift.json"))
    bad["schema_version"] = "BAD"
    with pytest.raises(V.VerificationError, match="schema_version"):
        V.verify_certificate(bad)
    bad["schema_version"] = V.SCHEMA_VERSION
    bad["mode"] = "bogus"
    with pytest.raises(V.VerificationError, match="Unknown verification mode"):
        V.verify_certificate(bad)
    with pytest.raises(V.VerificationError, match="regular file"):
        V.verify_file(tmp_path)
    big = tmp_path / "big.json"
    big.write_bytes(b" " * (V.MAX_JSON_BYTES + 1))
    with pytest.raises(V.VerificationError, match="size"):
        V.verify_file(big)
