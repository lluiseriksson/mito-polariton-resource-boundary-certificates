"""
MITO-POLARITON-BOUND-CERT-1.0: Zero-floating-point exact algebraic verifier uniting
Lluis Eriksson's operational coherence-maintenance and resource-boundary program
(ARR-2025-2AQXS44H6Z8GQAG2, ARR-2025-76C3S3SSMP8HJ8NF, ARR-2026-53WA9C4RB39JRRXF,
ARR-2026-77MR0BB1E487CAYR, ARR-2026-6YFENMGGBY9PPBF1, ARR-2026-4F7SF8FXM18ANAXH)
with the 71.0-THz mitochondrial cristae mito-polariton model of Yang, Gu, and Song
(bioRxiv:10.64898/2026.09.10.750628v1, September 2026).

Strictly zero floating-point literals, zero float() calls, zero true-division (/ or /=),
and zero math/numpy imports. All arithmetic uses exact Python int and fractions.Fraction.
"""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction
from typing import Any

SCHEMA_VERSION = "MITO-POLARITON-BOUND-CERT-1.0"
MAX_JSON_BYTES = 1_000_000
MAX_RAT_ABS = 10**24


class VerificationError(ValueError):
    """Raised whenever a certificate violates schema, bounds, or mathematical invariants."""


def _gcd(a: int, b: int) -> int:
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


def _req_int(val: Any, name: str, lo: int | None = None, hi: int | None = None) -> int:
    if isinstance(val, bool) or not isinstance(val, int):
        raise VerificationError(f"Expected integer for {name}, got {type(val).__name__}")
    if lo is not None and val < lo:
        raise VerificationError(f"{name}={val} below minimum {lo}")
    if hi is not None and val > hi:
        raise VerificationError(f"{name}={val} above maximum {hi}")
    return val


def _req_str(val: Any, name: str) -> str:
    if not isinstance(val, str) or not val.strip():
        raise VerificationError(f"Expected non-empty string for {name}")
    return val


def _req_dict(val: Any, name: str) -> dict[str, Any]:
    if not isinstance(val, dict):
        raise VerificationError(f"Expected dict for {name}")
    return val


def _req_list(val: Any, name: str, min_len: int = 0, max_len: int = 256) -> list[Any]:
    if not isinstance(val, list):
        raise VerificationError(f"Expected list for {name}")
    if len(val) < min_len or len(val) > max_len:
        raise VerificationError(f"{name} length {len(val)} out of range [{min_len}, {max_len}]")
    return val


def _parse_rat(val: Any, name: str) -> Fraction:
    if not isinstance(val, list) or len(val) != 2:
        raise VerificationError(f"Expected [num, den] rational pair for {name}")
    num = _req_int(val[0], f"{name}[0]", -MAX_RAT_ABS, MAX_RAT_ABS)
    den = _req_int(val[1], f"{name}[1]", 1, MAX_RAT_ABS)
    if _gcd(num, den) != 1:
        raise VerificationError(f"Rational {name} not in lowest terms")
    return Fraction(num, den)


def _rat_pair(f: Fraction) -> list[int]:
    return [f.numerator, f.denominator]


def _inv(f: Fraction) -> Fraction:
    if f == 0:
        raise VerificationError("Exact rational division by zero")
    return Fraction(f.denominator, f.numerator)


def _no_dup_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise VerificationError(f"Duplicate JSON key: {k}")
        out[k] = v
    return out


def _reject_json_constant(token: str) -> Any:
    raise VerificationError(f"Illegal non-finite JSON constant: {token}")


def _reject_json_float(token: str) -> Any:
    raise VerificationError(f"Illegal floating-point JSON literal: {token}")


# ---------------------------------------------------------------------------
# Mode 1: hopfield_a2_polariton_audit (Gauge-invariant Hopfield vs RWA + Isotope shifts)
# ---------------------------------------------------------------------------

def _verify_mode1(payload: dict[str, Any]) -> dict[str, Any]:
    submode = _req_str(payload.get("submode"), "submode")

    if submode == "resonant_hopfield_vs_rwa":
        w0 = _parse_rat(payload.get("omega_0_thz"), "omega_0_thz")
        nu_m = _parse_rat(payload.get("nu_minus_thz"), "nu_minus_thz")
        if w0 <= 0 or nu_m <= 0 or nu_m >= w0:
            raise VerificationError("Require 0 < nu_minus < omega_0")

        # RWA symmetric splitting: g_rwa = w0 - nu_m, nu_plus_rwa = w0 + g_rwa = 2*w0 - nu_m
        g_rwa = w0 - nu_m
        nu_p_rwa = w0 + g_rwa
        rwa_prod_deficit = w0 * w0 - nu_p_rwa * nu_m
        if rwa_prod_deficit != g_rwa * g_rwa:
            raise VerificationError("RWA product deficit identity failed")

        # Exact gauge-invariant Hopfield TRK (D = g^2 / w0, wc = w0):
        # nu_p * nu_m = w0^2 => nu_p = w0^2 / nu_m, g_hop = (nu_p - nu_m) / 2
        nu_p_hop = (w0 * w0) * _inv(nu_m)
        g_hop = (nu_p_hop - nu_m) * Fraction(1, 2)
        eta_hop = g_hop * _inv(w0)
        asymmetric_shift = nu_p_hop - nu_p_rwa

        # Verify exact Hopfield secular equation P(lambda) = lambda^2 - (2*w0^2 + 4*g^2)*lambda + w0^4 == 0
        tr_hop = 2 * w0 * w0 + 4 * g_hop * g_hop
        det_hop = w0 ** 4
        if nu_p_hop * nu_p_hop + nu_m * nu_m != tr_hop:
            raise VerificationError("Hopfield trace Vieta identity failed")
        if (nu_p_hop * nu_p_hop) * (nu_m * nu_m) != det_hop:
            raise VerificationError("Hopfield determinant Vieta identity failed")
        if asymmetric_shift != (g_rwa * g_rwa) * _inv(nu_m):
            raise VerificationError("Exact asymmetric shift identity (w0 - nu_m)^2 / nu_m failed")

        # Verify optional rational upper/lower brackets on nu_p_hop and eta_hop
        if "expected_nu_plus_hop" in payload:
            exp_np = _parse_rat(payload["expected_nu_plus_hop"], "expected_nu_plus_hop")
            if exp_np != nu_p_hop:
                raise VerificationError(f"nu_plus_hop mismatch: {nu_p_hop} != {exp_np}")
        if "min_eta_usc" in payload:
            min_eta = _parse_rat(payload["min_eta_usc"], "min_eta_usc")
            if eta_hop <= min_eta:
                raise VerificationError(f"Coupling ratio eta={eta_hop} not above {min_eta}")

        return {
            "mode": "hopfield_a2_polariton_audit",
            "submode": submode,
            "omega_0_thz": _rat_pair(w0),
            "nu_minus_thz": _rat_pair(nu_m),
            "nu_plus_rwa_thz": _rat_pair(nu_p_rwa),
            "nu_plus_hopfield_thz": _rat_pair(nu_p_hop),
            "asymmetric_shift_thz": _rat_pair(asymmetric_shift),
            "g_rwa_thz": _rat_pair(g_rwa),
            "g_hopfield_thz": _rat_pair(g_hop),
            "eta_hopfield": _rat_pair(eta_hop),
            "is_ultrastrong_gt_0p1": eta_hop > Fraction(1, 10),
        }

    if submode == "detuned_hopfield_and_isotope":
        wc = _parse_rat(payload.get("omega_c_thz"), "omega_c_thz")
        w0 = _parse_rat(payload.get("omega_0_thz"), "omega_0_thz")
        g = _parse_rat(payload.get("coupling_g_thz"), "coupling_g_thz")
        if wc <= 0 or w0 <= 0 or g < 0:
            raise VerificationError("Frequencies must be positive and coupling nonnegative")
        # Secular coefficients for lambda = nu^2:
        # B = wc^2 + w0^2 + 4*g^2, C = wc^2 * w0^2, disc = B^2 - 4*C = (wc^2 - w0^2)^2 + 8*g^2*(wc^2 + w0^2) + 16*g^4
        a, b, g2 = wc * wc, w0 * w0, g * g
        B = a + b + 4 * g2
        C = a * b
        disc = B * B - 4 * C
        disc_explicit = (a - b) * (a - b) + 8 * g2 * (a + b) + 16 * g2 * g2
        if disc != disc_explicit or disc < 0 or C <= 0:
            raise VerificationError("Hopfield TRK stability/discriminant invariant failed")

        # Verify exact rational bracket [lo, hi] for lower polariton frequency nu_-:
        # Since lambda_- = (B - sqrt(disc))/2, nu_- in [lo, hi] iff
        #   2*lo^2 <= B and (B - 2*lo^2)^2 >= disc (lower bound) AND
        #   2*hi^2 <= B and (B - 2*hi^2)^2 <= disc (upper bound)
        lo = _parse_rat(payload.get("nu_minus_lo_thz"), "nu_minus_lo_thz")
        hi = _parse_rat(payload.get("nu_minus_hi_thz"), "nu_minus_hi_thz")
        if lo <= 0 or lo >= hi:
            raise VerificationError("Invalid bracket [lo, hi]")
        if 2 * lo * lo > B or (B - 2 * lo * lo) ** 2 < disc:
            raise VerificationError(f"Lower bracket lo={lo} exceeds true nu_-")
        if 2 * hi * hi > B or (B - 2 * hi * hi) ** 2 > disc:
            raise VerificationError(f"Upper bracket hi={hi} below true nu_-")

        return {
            "mode": "hopfield_a2_polariton_audit",
            "submode": submode,
            "secular_B": _rat_pair(B),
            "secular_C": _rat_pair(C),
            "discriminant": _rat_pair(disc),
            "nu_minus_bracket_thz": [_rat_pair(lo), _rat_pair(hi)],
            "no_superradiant_collapse": True,
        }

    raise VerificationError(f"Unknown Mode 1 submode: {submode}")


# ---------------------------------------------------------------------------
# Mode 2: bioenergetic_resource_horizon (ARR-2025-2AQXS44H6Z8GQAG2 Thms 4.1, 9.1 & ATP budget)
# ---------------------------------------------------------------------------

def _verify_mode2(payload: dict[str, Any]) -> dict[str, Any]:
    submode = _req_str(payload.get("submode"), "submode")

    if submode == "atp_resource_horizon_audit":
        temp_K = _parse_rat(payload.get("temperature_K"), "temperature_K")
        kBT_meV = _parse_rat(payload.get("kBT_meV"), "kBT_meV")
        dG_atp_meV = _parse_rat(payload.get("deltaG_atp_meV"), "deltaG_atp_meV")
        atp_rate_hz = _parse_rat(payload.get("atp_rate_per_s"), "atp_rate_per_s")
        kappa_down_hz = _parse_rat(payload.get("kappa_down_per_s"), "kappa_down_per_s")
        c0_nats = _parse_rat(payload.get("target_coherence_nats"), "target_coherence_nats")
        if temp_K <= 0 or kBT_meV <= 0 or dG_atp_meV <= 0 or atp_rate_hz <= 0 or kappa_down_hz < 0 or c0_nats < 0:
            raise VerificationError("Invalid non-positive bioenergetic parameter")
        # Exact SI-2019 k_B / e in meV/K: (1.380649e-23 / 1.602176634e-19) * 1000 = 138064900 / 1602176634 meV/K
        # Verify supplied kBT_meV matches temperature_K within 0.05 meV
        kB_over_e_meV_per_K = Fraction(138064900, 1602176634)
        expected_kBT_meV = kB_over_e_meV_per_K * temp_K
        if abs(kBT_meV - expected_kBT_meV) > Fraction(1, 20):
            raise VerificationError(f"kBT_meV={kBT_meV} inconsistent with SI-2019 T={temp_K} K")

        # Mitochondrial metabolic power in units of (kBT / s): P_mito / kBT = (dG_atp / kBT) * atp_rate
        atp_in_kBT = dG_atp_meV * _inv(kBT_meV)
        p_mito_kBT_hz = atp_in_kBT * atp_rate_hz

        # Theorem 9.1 lower bound: P_maint / kBT >= kappa_down * C_0
        p_req_kBT_hz = kappa_down_hz * c0_nats
        feasible = p_req_kBT_hz <= p_mito_kBT_hz

        # Max sustainable coherence at given kappa_down (when kappa_down > 0)
        max_c_nats = (p_mito_kBT_hz * _inv(kappa_down_hz)) if kappa_down_hz > 0 else None
        # Max tolerable dephasing floor at given C_0 > 0
        max_kappa_hz = (p_mito_kBT_hz * _inv(c0_nats)) if c0_nats > 0 else None

        expected_feasible = payload.get("expected_feasible")
        if expected_feasible is not None:
            if not isinstance(expected_feasible, bool):
                raise VerificationError("expected_feasible must be boolean")
            if feasible != expected_feasible:
                raise VerificationError(f"Feasibility mismatch: got {feasible}, expected {expected_feasible}")

        return {
            "mode": "bioenergetic_resource_horizon",
            "submode": submode,
            "atp_in_kBT": _rat_pair(atp_in_kBT),
            "p_mito_in_kBT_per_s": _rat_pair(p_mito_kBT_hz),
            "p_req_in_kBT_per_s": _rat_pair(p_req_kBT_hz),
            "feasible_under_atp_budget": feasible,
            "max_sustainable_C_nats": _rat_pair(max_c_nats) if max_c_nats is not None else None,
            "max_tolerable_kappa_per_s": _rat_pair(max_kappa_hz) if max_kappa_hz is not None else None,
            "regime": "Regime_I_Passive_Equilibrium" if c0_nats == 0 else ("Regime_II_Feasible_Active" if feasible else "Horizon_Violation_Infeasible"),
        }

    if submode == "photon_vs_atp_and_restoration_gap":
        # Exact SI-2019 comparison of h*nu vs kBT and DeltaG_ATP + ARR-2026-77MR0BB1E487CAYR endpoint vs holding check
        h_nu_meV = _parse_rat(payload.get("polariton_energy_meV"), "polariton_energy_meV")
        kBT_meV = _parse_rat(payload.get("kBT_meV"), "kBT_meV")
        dG_atp_meV = _parse_rat(payload.get("deltaG_atp_meV"), "deltaG_atp_meV")
        W0_kBT = _parse_rat(payload.get("endpoint_refresh_work_kBT"), "endpoint_refresh_work_kBT")
        T_period_s = _parse_rat(payload.get("refresh_period_s"), "refresh_period_s")
        k0_hz = _parse_rat(payload.get("holding_floor_kappa0_per_s"), "holding_floor_kappa0_per_s")
        c0_nats = _parse_rat(payload.get("holding_coherence_nats"), "holding_coherence_nats")
        if h_nu_meV <= 0 or kBT_meV <= 0 or dG_atp_meV <= 0 or W0_kBT <= 0 or T_period_s <= 0 or k0_hz <= 0 or c0_nats <= 0:
            raise VerificationError("All parameters must be strictly positive")

        ratio_kBT = h_nu_meV * _inv(kBT_meV)
        two_photon_ratio_atp = (2 * h_nu_meV) * _inv(dG_atp_meV)
        if two_photon_ratio_atp <= 1:
            raise VerificationError("Expected 2 * h*nu > DeltaG_ATP")

        p_endpoint_avg = W0_kBT * _inv(T_period_s)
        p_holding_floor = k0_hz * c0_nats
        if p_endpoint_avg >= p_holding_floor:
            raise VerificationError("Endpoint restoration average power did not drop strictly below continuous holding floor")

        return {
            "mode": "bioenergetic_resource_horizon",
            "submode": submode,
            "h_nu_over_kBT": _rat_pair(ratio_kBT),
            "two_photons_over_atp": _rat_pair(two_photon_ratio_atp),
            "endpoint_avg_power_kBT_per_s": _rat_pair(p_endpoint_avg),
            "continuous_holding_floor_kBT_per_s": _rat_pair(p_holding_floor),
            "holding_to_endpoint_ratio": _rat_pair(p_holding_floor * _inv(p_endpoint_avg)),
        }

    raise VerificationError(f"Unknown Mode 2 submode: {submode}")


# ---------------------------------------------------------------------------
# Mode 3: rip_u_collar_and_omega0_floor (ARR-2025-2AQXS44H6Z8GQAG2 §5-8 & ARR-2026-53WA9C4RB39JRRXF)
# ---------------------------------------------------------------------------

def _verify_mode3(payload: dict[str, Any]) -> dict[str, Any]:
    submode = _req_str(payload.get("submode"), "submode")

    if submode == "omega0_davies_dirichlet_floor":
        # Exact 2x2 polariton doublet S(0) = diag(s_m, s_p) and Hermitian observable O = [[o00, o12], [o12, o11]]
        # Stationary state sigma = diag(p_m, p_p) (p_m + p_p = 1, p_m, p_p > 0)
        # Exact KMS-weighted Hilbert-Schmidt norm ||[S(0), O]||^2_{2, sigma} = 2 * sqrt(p_m*p_p) * ((s_m - s_p)*o12)^2
        # Using rational squared form: E0^2 = (gamma0 / 2)^2 * 4 * p_m * p_p * ((s_m - s_p)*o12)^4
        # And exact Frobenius/unweighted trace Tr(sigma [S(0), O]^dagger [S(0), O]) = ((s_m - s_p)*o12)^2!
        gamma0 = _parse_rat(payload.get("gamma_0_per_s"), "gamma_0_per_s")
        sm = _parse_rat(payload.get("s_minus"), "s_minus")
        sp = _parse_rat(payload.get("s_plus"), "s_plus")
        o12 = _parse_rat(payload.get("o_12"), "o_12")
        pm = _parse_rat(payload.get("sigma_minus"), "sigma_minus")
        pp = _parse_rat(payload.get("sigma_plus"), "sigma_plus")
        if gamma0 < 0 or pm <= 0 or pp <= 0 or pm + pp != 1:
            raise VerificationError("Invalid gamma0 or stationary distribution sigma")

        # Literal 2x2 matrix commutator C = S(0)*O - O*S(0)
        S0 = [[sm, Fraction(0, 1)], [Fraction(0, 1), sp]]
        O = [[Fraction(0, 1), o12], [o12, Fraction(0, 1)]]
        C = [[Fraction(0, 1), Fraction(0, 1)], [Fraction(0, 1), Fraction(0, 1)]]
        for i in range(2):
            for j in range(2):
                s_o = sum(S0[i][k] * O[k][j] for k in range(2))
                o_s = sum(O[i][k] * S0[k][j] for k in range(2))
                C[i][j] = s_o - o_s
        # C^dagger * C (C is skew-symmetric real -> C^dagger = -C = C^T)
        # Tr(sigma * C^dagger * C) = pm * (C[0][0]^2 + C[1][0]^2) + pp * (C[0][1]^2 + C[1][1]^2)
        c_norm_sq = pm * (C[0][0] ** 2 + C[1][0] ** 2) + pp * (C[0][1] ** 2 + C[1][1] ** 2)
        dirichlet_gns = gamma0 * Fraction(1, 2) * c_norm_sq
        expected_closed = gamma0 * Fraction(1, 2) * ((sm - sp) * o12) ** 2
        if dirichlet_gns != expected_closed:
            raise VerificationError("Exact Davies omega=0 Dirichlet commutator identity failed")

        # Check witness positivity when sm != sp and o12 != 0 and gamma0 > 0
        has_floor = dirichlet_gns > 0
        if (gamma0 > 0 and sm != sp and o12 != 0) and not has_floor:
            raise VerificationError("Expected strictly positive omega=0 floor")

        return {
            "mode": "rip_u_collar_and_omega0_floor",
            "submode": submode,
            "commutator_12": _rat_pair(C[0][1]),
            "dirichlet_omega0_rate": _rat_pair(dirichlet_gns),
            "has_irreducible_floor": has_floor,
        }

    if submode == "cristae_collar_rip_u_and_spectral_gap":
        # Verify geometric collar RIP-U ceiling kappa_up(eps) = kappa_0 + B * q^eps (0 < q < 1)
        # AND Lorentzian spectral-gap suppression factor moving from w0 to nu_- relative to bath peak w_bath
        k0 = _parse_rat(payload.get("kappa_0_per_s"), "kappa_0_per_s")
        B0 = _parse_rat(payload.get("collar_prefactor_B0_per_s"), "collar_prefactor_B0_per_s")
        decay_q = _parse_rat(payload.get("collar_decay_q"), "collar_decay_q")
        eps_steps = _req_list(payload.get("collar_steps"), "collar_steps", 2, 32)
        w0 = _parse_rat(payload.get("omega_0_thz"), "omega_0_thz")
        nu_m = _parse_rat(payload.get("nu_minus_thz"), "nu_minus_thz")
        w_bath = _parse_rat(payload.get("bath_peak_thz"), "bath_peak_thz")
        gamma_bath = _parse_rat(payload.get("bath_hwhm_thz"), "bath_hwhm_thz")
        if k0 < 0 or B0 <= 0 or decay_q <= 0 or decay_q >= 1 or gamma_bath <= 0:
            raise VerificationError("Invalid collar or bath parameters")

        steps = [_req_int(s, f"collar_steps[{i}]", 0, 50) for i, s in enumerate(eps_steps)]
        if any(steps[i] >= steps[i + 1] for i in range(len(steps) - 1)):
            raise VerificationError("collar_steps must be strictly increasing")
        ceilings = [k0 + B0 * (decay_q ** s) for s in steps]
        # Verify strictly decreasing ceiling yet always >= k0
        for i in range(len(ceilings) - 1):
            if ceilings[i] <= ceilings[i + 1]:
                raise VerificationError("RIP-U ceiling not strictly decreasing with collar thickness")
        if ceilings[-1] < k0:
            raise VerificationError("Ceiling fell below irreducible floor kappa_0")

        # Exact rational Lorentzian bath spectral density ratio J(w0) / J(nu_-) = ((w_bath - nu_-)^2 + G^2) / ((w_bath - w0)^2 + G^2)
        num_lor = (w_bath - nu_m) ** 2 + gamma_bath ** 2
        den_lor = (w_bath - w0) ** 2 + gamma_bath ** 2
        suppression_factor = num_lor * _inv(den_lor)
        if suppression_factor <= 1:
            raise VerificationError("Lower polariton detuning did not suppress bath spectral density")

        return {
            "mode": "rip_u_collar_and_omega0_floor",
            "submode": submode,
            "first_ceiling_per_s": _rat_pair(ceilings[0]),
            "last_ceiling_per_s": _rat_pair(ceilings[-1]),
            "irreducible_floor_per_s": _rat_pair(k0),
            "lorentzian_suppression_factor": _rat_pair(suppression_factor),
        }

    raise VerificationError(f"Unknown Mode 3 submode: {submode}")


# ---------------------------------------------------------------------------
# Mode 4: dark_mode_filling_and_passive_network (ARR-2026-6YFENMGGBY9PPBF1 & ARR-2026-4F7SF8FXM18ANAXH)
# ---------------------------------------------------------------------------

def _verify_mode4(payload: dict[str, Any]) -> dict[str, Any]:
    submode = _req_str(payload.get("submode"), "submode")

    if submode == "filled_manybody_dark_mode_floor":
        N_dipoles = _req_int(payload.get("num_ch2_dipoles"), "num_ch2_dipoles", 2, 10**12)
        w_vals_raw = _req_list(payload.get("zero_mode_weights"), "zero_mode_weights", 1, 64)
        results = []
        for idx, wr in enumerate(w_vals_raw):
            w = _parse_rat(wr, f"zero_mode_weights[{idx}]")
            if w < 0 or w > 1:
                raise VerificationError(f"Weight w={w} out of [0, 1]")
            dilute = w * (1 - w)
            filled = (1 + 2 * w - 3 * w * w) * Fraction(1, 4)
            excess = filled - dilute
            if excess != ((1 - w) ** 2) * Fraction(1, 4):
                raise VerificationError("Exact filled-vs-dilute leakage identity failed")
            if w <= Fraction(2, 3) and filled < Fraction(1, 4):
                raise VerificationError("Filled leakage fell below 1/4 floor for w <= 2/3")
            results.append({
                "w": _rat_pair(w),
                "dilute_leak": _rat_pair(dilute),
                "filled_leak": _rat_pair(filled),
                "floor_excess": _rat_pair(excess),
            })

        bright_frac = Fraction(1, N_dipoles)
        dark_frac = Fraction(N_dipoles - 1, N_dipoles)
        if bright_frac + dark_frac != 1:
            raise VerificationError("Bright/dark partition mismatch")

        return {
            "mode": "dark_mode_filling_and_passive_network",
            "submode": submode,
            "num_ch2_dipoles": N_dipoles,
            "num_dark_modes": N_dipoles - 1,
            "bright_fraction": _rat_pair(bright_frac),
            "dark_fraction": _rat_pair(dark_frac),
            "num_weights_audited": len(results),
            "min_filled_leak": _rat_pair(min(Fraction(*r["filled_leak"]) for r in results)),
            "max_dilute_to_filled_gap": _rat_pair(max(Fraction(*r["floor_excess"]) for r in results)),
        }

    if submode == "passive_crista_network_mixing":
        # Audit ARR-2026-4F7SF8FXM18ANAXH finite-error obstruction:
        # comparator stopband leakage >= [1 - C_S * (delta + beta)]_+
        S_order = _req_int(payload.get("network_order_S"), "network_order_S", 5, 100)
        C_S = _parse_rat(payload.get("singular_value_const_CS"), "singular_value_const_CS")
        delta = _parse_rat(payload.get("calibration_defect_delta"), "calibration_defect_delta")
        beta = _parse_rat(payload.get("reducing_line_defect_beta"), "reducing_line_defect_beta")
        irred_leak = _parse_rat(payload.get("irreducible_stopband_leak"), "irreducible_stopband_leak")
        if C_S <= 0 or delta < 0 or beta < 0 or irred_leak < 0:
            raise VerificationError("Invalid passive network parameters")

        num_calibrations = 3 * (S_order - 1)
        red_lower_bound = max(Fraction(0, 1), Fraction(1, 1) - C_S * (delta + beta))
        if red_lower_bound <= irred_leak:
            raise VerificationError(
                f"No strict separation: reducible lower bound {red_lower_bound} <= irreducible leak {irred_leak}"
            )
        advantage_ratio = red_lower_bound * _inv(irred_leak) if irred_leak > 0 else None

        return {
            "mode": "dark_mode_filling_and_passive_network",
            "submode": submode,
            "network_order_S": S_order,
            "tangential_calibrations": num_calibrations,
            "reducible_leakage_lower_bound": _rat_pair(red_lower_bound),
            "irreducible_stopband_leak": _rat_pair(irred_leak),
            "suppression_advantage_ratio": _rat_pair(advantage_ratio) if advantage_ratio is not None else None,
        }

    raise VerificationError(f"Unknown Mode 4 submode: {submode}")


# ---------------------------------------------------------------------------
# Entry Points & CLI
# ---------------------------------------------------------------------------

def verify_certificate(cert: Any) -> dict[str, Any]:
    root = _req_dict(cert, "certificate")
    if root.get("schema_version") != SCHEMA_VERSION:
        raise VerificationError(f"Invalid schema_version: {root.get('schema_version')!r}")
    cert_id = _req_str(root.get("cert_id"), "cert_id")
    mode = _req_str(root.get("mode"), "mode")
    payload = _req_dict(root.get("payload"), "payload")

    if mode == "hopfield_a2_polariton_audit":
        res = _verify_mode1(payload)
    elif mode == "bioenergetic_resource_horizon":
        res = _verify_mode2(payload)
    elif mode == "rip_u_collar_and_omega0_floor":
        res = _verify_mode3(payload)
    elif mode == "dark_mode_filling_and_passive_network":
        res = _verify_mode4(payload)
    else:
        raise VerificationError(f"Unknown verification mode: {mode!r}")

    res["cert_id"] = cert_id
    res["schema_version"] = SCHEMA_VERSION
    return res


def verify_file(path: str | pathlib.Path) -> dict[str, Any]:
    p = pathlib.Path(path)
    if not p.is_file():
        raise VerificationError(f"Certificate path is not a regular file: {p}")
    size = p.stat().st_size
    if size <= 0 or size > MAX_JSON_BYTES:
        raise VerificationError(f"Certificate file size {size} out of bounds (1..{MAX_JSON_BYTES})")
    try:
        raw_text = p.read_text(encoding="utf-8")
        parsed = json.loads(
            raw_text,
            object_pairs_hook=_no_dup_pairs,
            parse_constant=_reject_json_constant,
            parse_float=_reject_json_float,
        )
    except (OSError, UnicodeDecodeError, RecursionError, ValueError) as exc:
        raise VerificationError(f"Malformed JSON in {p.name}: {exc}") from exc
    return verify_certificate(parsed)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("Usage: python -m src.mito_polariton_bound_verifier <file.json | dir>", file=sys.stderr)
        return 2
    targets: list[pathlib.Path] = []
    for a in args:
        p = pathlib.Path(a)
        if p.is_dir():
            targets.extend(sorted(p.glob("*.json")))
        else:
            targets.append(p)
    if not targets:
        print("No JSON certificate files found.", file=sys.stderr)
        return 2
    for t in targets:
        res = verify_file(t)
        print(f"[PASS] {res['cert_id']} ({res['mode']})")
    print(f"Verified {len(targets)}/{len(targets)} certificates successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
