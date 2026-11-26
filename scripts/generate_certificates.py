"""Generate all 16 canonical zero-float JSON certificates (C01-C16) for MITO-POLARITON-BOUND-CERT-1.0."""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mito_polariton_bound_verifier import SCHEMA_VERSION, verify_file

CERTS_DIR = ROOT / "certificates"
CERTS_DIR.mkdir(parents=True, exist_ok=True)


def _write(fname: str, obj: dict) -> pathlib.Path:
    p = CERTS_DIR / fname
    p.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8", newline="\n")
    return p


def main() -> int:
    certs: list[tuple[str, dict]] = [
        # Mode 1: Hopfield A^2 polariton vs RWA & isotope/detuned checks (C01-C04)
        (
            "C01_mito_71_87_hopfield_trk_shift.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C01",
                "mode": "hopfield_a2_polariton_audit",
                "payload": {
                    "submode": "resonant_hopfield_vs_rwa",
                    "omega_0_thz": [87, 1],
                    "nu_minus_thz": [71, 1],
                    "expected_nu_plus_hop": [7569, 71],
                    "min_eta_usc": [1, 5],
                },
            },
        ),
        (
            "C02_mito_strong_coupling_baseline.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C02",
                "mode": "hopfield_a2_polariton_audit",
                "payload": {
                    "submode": "resonant_hopfield_vs_rwa",
                    "omega_0_thz": [87, 1],
                    "nu_minus_thz": [79, 1],
                    "expected_nu_plus_hop": [7569, 79],
                    "min_eta_usc": [1, 11],
                },
            },
        ),
        (
            "C03_cd2_deuterated_lipid_polariton.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C03",
                "mode": "hopfield_a2_polariton_audit",
                "payload": {
                    "submode": "detuned_hopfield_and_isotope",
                    "omega_c_thz": [87, 1],
                    "omega_0_thz": [123, 2],  # 61.5 THz CD2 stretch
                    "coupling_g_thz": [15, 1],
                    "nu_minus_lo_thz": [56, 1],
                    "nu_minus_hi_thz": [57, 1],
                },
            },
        ),
        (
            "C04_ultrastrong_detuned_crista_cavity.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C04",
                "mode": "hopfield_a2_polariton_audit",
                "payload": {
                    "submode": "detuned_hopfield_and_isotope",
                    "omega_c_thz": [90, 1],
                    "omega_0_thz": [87, 1],
                    "coupling_g_thz": [18, 1],
                    "nu_minus_lo_thz": [72, 1],
                    "nu_minus_hi_thz": [73, 1],
                },
            },
        ),
        # Mode 2: Bioenergetic Resource Horizon & Endpoint vs Holding (C05-C08)
        (
            "C05_regime1_passive_equilibrium_zero_cost.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C05",
                "mode": "bioenergetic_resource_horizon",
                "payload": {
                    "submode": "atp_resource_horizon_audit",
                    "temperature_K": [310, 1],
                    "kBT_meV": [2671, 100],
                    "deltaG_atp_meV": [2591, 5],
                    "atp_rate_per_s": [100000, 1],
                    "kappa_down_per_s": [1000000000000, 1],
                    "target_coherence_nats": [0, 1],
                    "expected_feasible": True,
                },
            },
        ),
        (
            "C06_horizon_violation_bulk_water_dephasing.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C06",
                "mode": "bioenergetic_resource_horizon",
                "payload": {
                    "submode": "atp_resource_horizon_audit",
                    "temperature_K": [310, 1],
                    "kBT_meV": [2671, 100],
                    "deltaG_atp_meV": [2591, 5],
                    "atp_rate_per_s": [100000, 1],
                    "kappa_down_per_s": [1000000000000, 1],
                    "target_coherence_nats": [1, 1],
                    "expected_feasible": False,
                },
            },
        ),
        (
            "C07_regime2_microsecond_suppressed_feasible.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C07",
                "mode": "bioenergetic_resource_horizon",
                "payload": {
                    "submode": "atp_resource_horizon_audit",
                    "temperature_K": [310, 1],
                    "kBT_meV": [2671, 100],
                    "deltaG_atp_meV": [2591, 5],
                    "atp_rate_per_s": [100000, 1],
                    "kappa_down_per_s": [1000000, 1],  # 1 us coherence time
                    "target_coherence_nats": [1, 1],
                    "expected_feasible": True,
                },
            },
        ),
        (
            "C08_two_photon_atp_and_restoration_vs_holding.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C08",
                "mode": "bioenergetic_resource_horizon",
                "payload": {
                    "submode": "photon_vs_atp_and_restoration_gap",
                    "polariton_energy_meV": [1468, 5],
                    "kBT_meV": [2671, 100],
                    "deltaG_atp_meV": [2591, 5],
                    "endpoint_refresh_work_kBT": [10, 1],
                    "refresh_period_s": [1, 100],  # 10 ms refresh -> 1000 kBT/s avg
                    "holding_floor_kappa0_per_s": [1000000, 1],
                    "holding_coherence_nats": [1, 1],
                },
            },
        ),
        # Mode 3: RIP-U Cristae Collar & omega=0 Davies Dirichlet Floor (C09-C12)
        (
            "C09_omega0_dirichlet_floor_active.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C09",
                "mode": "rip_u_collar_and_omega0_floor",
                "payload": {
                    "submode": "omega0_davies_dirichlet_floor",
                    "gamma_0_per_s": [1000000, 1],
                    "s_minus": [3, 2],
                    "s_plus": [-1, 2],
                    "o_12": [1, 1],
                    "sigma_minus": [4, 5],
                    "sigma_plus": [1, 5],
                },
            },
        ),
        (
            "C10_omega0_dirichlet_commuting_vanishes.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C10",
                "mode": "rip_u_collar_and_omega0_floor",
                "payload": {
                    "submode": "omega0_davies_dirichlet_floor",
                    "gamma_0_per_s": [1000000, 1],
                    "s_minus": [1, 1],
                    "s_plus": [1, 1],
                    "o_12": [1, 1],
                    "sigma_minus": [1, 2],
                    "sigma_plus": [1, 2],
                },
            },
        ),
        (
            "C11_cristae_collar_rip_u_with_floor.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C11",
                "mode": "rip_u_collar_and_omega0_floor",
                "payload": {
                    "submode": "cristae_collar_rip_u_and_spectral_gap",
                    "kappa_0_per_s": [500000, 1],
                    "collar_prefactor_B0_per_s": [1000000000000, 1],
                    "collar_decay_q": [1, 10],
                    "collar_steps": [0, 2, 4, 6, 8],
                    "omega_0_thz": [87, 1],
                    "nu_minus_thz": [71, 1],
                    "bath_peak_thz": [95, 1],
                    "bath_hwhm_thz": [8, 1],
                },
            },
        ),
        (
            "C12_deep_collar_spectral_gap_narrow_bath.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C12",
                "mode": "rip_u_collar_and_omega0_floor",
                "payload": {
                    "submode": "cristae_collar_rip_u_and_spectral_gap",
                    "kappa_0_per_s": [100000, 1],
                    "collar_prefactor_B0_per_s": [100000000000, 1],
                    "collar_decay_q": [1, 4],
                    "collar_steps": [1, 3, 5, 7, 9],
                    "omega_0_thz": [87, 1],
                    "nu_minus_thz": [71, 1],
                    "bath_peak_thz": [100, 1],
                    "bath_hwhm_thz": [5, 1],
                },
            },
        ),
        # Mode 4: Bosonic Hopfield-Dicke Dark-Mode Leakage & Passive Multi-Crista Stack (C13-C16)
        (
            "C13_bosonic_dark_mode_leakage_71thz_10e6.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C13",
                "mode": "dark_mode_filling_and_passive_network",
                "payload": {
                    "submode": "bosonic_hopfield_dark_mode_leakage",
                    "num_ch2_dipoles": 1000000,
                    "omega_0_thz": [87, 1],
                    "nu_minus_thz": [71, 1],
                    "temperature_K": [310, 1],
                    "thermal_occ_upper_bound": [1, 500000],
                },
            },
        ),
        (
            "C14_bosonic_dark_mode_leakage_79thz_10e8.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C14",
                "mode": "dark_mode_filling_and_passive_network",
                "payload": {
                    "submode": "bosonic_hopfield_dark_mode_leakage",
                    "num_ch2_dipoles": 100000000,
                    "omega_0_thz": [87, 1],
                    "nu_minus_thz": [79, 1],
                    "temperature_K": [310, 1],
                    "thermal_occ_upper_bound": [1, 500000],
                },
            },
        ),
        (
            "C15_passive_network_S5_irreducible_gap.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C15",
                "mode": "dark_mode_filling_and_passive_network",
                "payload": {
                    "submode": "passive_crista_network_mixing",
                    "network_order_S": 5,
                    "crista_spacing_nm": [30, 1],
                    "singular_value_const_CS": [12, 1],
                    "calibration_defect_delta": [1, 100],
                    "reducing_line_defect_beta": [1, 100],
                    "irreducible_stopband_leak": [1, 100],
                },
            },
        ),
        (
            "C16_passive_network_S9_multi_crista_stack.json",
            {
                "schema_version": SCHEMA_VERSION,
                "cert_id": "C16",
                "mode": "dark_mode_filling_and_passive_network",
                "payload": {
                    "submode": "passive_crista_network_mixing",
                    "network_order_S": 9,
                    "crista_spacing_nm": [25, 1],
                    "singular_value_const_CS": [25, 1],
                    "calibration_defect_delta": [1, 200],
                    "reducing_line_defect_beta": [1, 200],
                    "irreducible_stopband_leak": [1, 1000],
                },
            },
        ),
    ]

    for fname, obj in certs:
        p = _write(fname, obj)
        res = verify_file(p)
        print(f"[OK] {res['cert_id']} -> {fname}")
    print(f"Generated and verified {len(certs)} certificates in {CERTS_DIR}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
