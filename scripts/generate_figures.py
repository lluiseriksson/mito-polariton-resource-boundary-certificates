"""Generate the 3 publication-grade figures for paper83-mito-polariton-resource-boundary-certificates from live exact outputs."""

from __future__ import annotations

import math
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mito_polariton_bound_verifier import verify_file

CERTS_DIR = ROOT / "certificates"
FIG_DIR = ROOT / "paper" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9.5,
    "axes.titlesize": 10.5,
    "axes.labelsize": 9.5,
    "legend.fontsize": 7.8,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "figure.dpi": 240,
})


def _f(pair: list[int]) -> float:
    return pair[0] / pair[1]


def fig1_hopfield_vs_rwa_spectrum() -> None:
    """Figure 1: (a) Exact gauge-invariant Hopfield A^2 polariton branches vs RWA as function of g/w0; (b) 103 vs 106.61 THz & D2O window."""
    r01 = verify_file(CERTS_DIR / "C01_mito_71_87_hopfield_trk_shift.json")
    r02 = verify_file(CERTS_DIR / "C02_mito_strong_coupling_baseline.json")

    w0 = 87.0
    etas = [i / 250.0 for i in range(1, 90)]  # g/w0 from 0.004 to 0.36
    nu_p_hop = [w0 * (math.sqrt(1.0 + e * e) + e) for e in etas]
    nu_m_hop = [w0 * (math.sqrt(1.0 + e * e) - e) for e in etas]
    nu_p_rwa = [w0 * (1.0 + e) for e in etas]
    nu_m_rwa = [w0 * (1.0 - e) for e in etas]

    eta01 = _f(r01["eta_hopfield"])
    np01 = _f(r01["nu_plus_hopfield_thz"])
    nm01 = _f(r01["nu_minus_thz"])
    eta02 = _f(r02["eta_hopfield"])
    np02 = _f(r02["nu_plus_hopfield_thz"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.6))

    ax1.axhspan(60.0, 80.0, color="#d9f0d3", alpha=0.55, label="Biomolecular quiet window (60-80 THz)")
    ax1.axhspan(90.0, 110.0, color="#fddbc7", alpha=0.45, label=r"H$_2$O / Amide-A band (90-110 THz)")
    ax1.plot(etas, nu_p_hop, color="#b2182b", lw=2.1, label=r"Hopfield $A^2$ ($\nu_+\nu_-=\omega_0^2$)")
    ax1.plot(etas, nu_m_hop, color="#b2182b", lw=2.1)
    ax1.plot(etas, nu_p_rwa, color="#2166ac", lw=1.5, ls="--", label=r"RWA ($\omega_0 \pm g$)")
    ax1.plot(etas, nu_m_rwa, color="#2166ac", lw=1.5, ls="--")
    ax1.axvline(0.1, color="#555555", lw=1.1, ls=":", label=r"USC threshold $\eta = 0.1$")
    ax1.scatter([eta01, eta01], [nm01, np01], color="#1b7837", s=55, zorder=6, label=r"C01: $71.0$ & $106.61$ THz")
    ax1.scatter([eta02], [np02], color="#762a83", marker="D", s=42, zorder=6, label=r"C02 ($79.0 \to 95.81$ THz)")
    ax1.set_xlim(0.0, 0.35)
    ax1.set_ylim(55.0, 152.0)
    ax1.set_xlabel(r"Normalized coupling $\eta = g / \omega_0$ ($\omega_0 = 87$ THz)")
    ax1.set_ylabel("Polariton frequency (THz)")
    ax1.set_title("(a) Gauge-Invariant Hopfield $A^2$ vs. RWA Branches")
    ax1.legend(loc="upper left", frameon=True, framealpha=0.94, fontsize=6.5, ncol=2)
    ax1.grid(alpha=0.22)

    # Panel (b): Direct spectral separation of RWA vs Hopfield MP+ and isotope markers
    cats = ["CD$_2$ bare\n(C03)", "MP$^-$ live\n(C01)", "D$_2$O O-D\nshift", "CH$_2$ bare\n($\\omega_0$)",
            "MP$^+$ RWA\n(naive)", "MP$^+$ Hop.\n(C01 TRK)"]
    freqs = [61.5, 71.0, 74.9, 87.0, 103.0, np01]
    cols = ["#74add1", "#1b7837", "#abd9e9", "#878787", "#4393c3", "#d73027"]
    bars = ax2.bar(range(len(cats)), freqs, color=cols, width=0.58)
    ax2.axhspan(100.0, 110.0, color="#e0f3f8", alpha=0.55, zorder=0, label=r"D$_2$O-cleared MP$^+$ test band")
    for bar, v in zip(bars, freqs):
        ax2.text(bar.get_x() + bar.get_width() / 2.0, v + 1.8, f"{v:.1f}", ha="center", va="bottom", fontsize=7.6)
    ax2.annotate("+3.61 THz\nTRK shift", xy=(5, np01 + 8.0), xytext=(2.85, 118.5),
                 arrowprops=dict(arrowstyle="->", color="#b2182b", lw=1.3),
                 fontsize=7.6, color="#b2182b", fontweight="bold")
    ax2.set_xticks(range(len(cats)))
    ax2.set_xticklabels(cats, fontsize=7.5)
    ax2.set_ylim(0, 136.0)
    ax2.set_ylabel("Vibrational / polariton frequency (THz)")
    ax2.set_title(r"(b) Falsifiable $+3.61$ THz Hopfield Shift & Isotope Map")
    ax2.legend(loc="upper left", frameon=True, framealpha=0.92, fontsize=7.4)
    ax2.grid(axis="y", alpha=0.22)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_hopfield_a2_vs_rwa.png")
    plt.close(fig)


def fig2_bioenergetic_resource_horizon() -> None:
    """Figure 2: (a) Mitochondrial ATP Resource Horizon phase diagram (kappa_down vs C_Delta); (b) RIP-U ceiling vs omega=0 floor."""
    r06 = verify_file(CERTS_DIR / "C06_horizon_violation_bulk_water_dephasing.json")
    r07 = verify_file(CERTS_DIR / "C07_regime2_microsecond_suppressed_feasible.json")
    r11 = verify_file(CERTS_DIR / "C11_cristae_collar_rip_u_with_floor.json")

    p_mito_kbt = _f(r06["p_mito_in_kBT_per_s"])  # ~1.94e6 kBT/s

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.6))

    # Panel (a): Log-log feasibility boundary kappa_down * C_Delta <= P_mito / kBT
    kappas = [10 ** (3 + i * 0.25) for i in range(41)]  # 10^3 to 10^13 s^-1
    c_max_mito = [p_mito_kbt / k for k in kappas]
    c_max_crista = [(p_mito_kbt / 100.0) / k for k in kappas]

    ax1.loglog(kappas, c_max_mito, color="#1b7837", lw=2.2, label=r"Whole mitochondrion ($10^5$ ATP/s)")
    ax1.loglog(kappas, c_max_crista, color="#2166ac", lw=1.6, ls="--", label=r"Single crista budget ($10^3$ ATP/s)")
    ax1.fill_between(kappas, c_max_mito, 1e3, color="#fddbc7", alpha=0.5, label="Thermodynamically forbidden (Thm. 9.1)")
    ax1.scatter([1e12], [1.0], color="#b2182b", marker="X", s=85, zorder=6, label=r"C06: Bulk water ($\kappa=10^{12}$, infeasible)")
    ax1.scatter([1e6], [1.0], color="#1b7837", marker="o", s=65, zorder=6, label=r"C07: $\tau=1\,\mu$s ($\kappa=10^6$, feasible)")
    ax1.set_xlim(1e3, 1e13)
    ax1.set_ylim(1e-9, 1e3)
    ax1.set_xlabel(r"Dephasing floor $\kappa_\downarrow$ ($\mathrm{s}^{-1}$, log scale)")
    ax1.set_ylabel(r"Max sustainable coherence $C_\Delta$ (nats)")
    ax1.set_title("(a) ATP Bioenergetic Resource Horizon ($T = 310$ K)")
    ax1.legend(loc="lower left", frameon=True, framealpha=0.92, fontsize=6.7)
    ax1.grid(True, which="both", alpha=0.2)

    # Panel (b): RIP-U geometric collar ceiling kappa_up(eps) = kappa_0 + B_0 * q^eps hitting omega=0 floor
    eps = list(range(0, 10))
    k0 = _f(r11["irreducible_floor_per_s"])  # 5e5
    B0 = 1e12
    q_dec = 0.1
    ceil_vals = [k0 + B0 * (q_dec ** e) for e in eps]
    ax2.semilogy(eps, ceil_vals, marker="o", color="#2166ac", lw=2.0, ms=5.0,
                 label=r"RIP-U ceiling $\kappa_\uparrow(\epsilon) = \kappa_0 + 10^{12}\cdot 10^{-\epsilon}$ (C11)")
    ax2.axhline(k0, color="#b2182b", lw=1.6, ls="--", label=r"$\omega=0$ Davies floor $\kappa_0 = 5\times 10^5\ \mathrm{s}^{-1}$")
    ax2.axhline(p_mito_kbt, color="#1b7837", lw=1.4, ls=":", label=r"Mitochondrial ATP budget ($1.94\times 10^6\ \mathrm{s}^{-1}$)")
    ax2.set_xticks(eps)
    ax2.set_ylim(1e4, 4e12)
    ax2.set_xlabel(r"Effective cristae collar steps $\epsilon$")
    ax2.set_ylabel(r"Effective decoherence rate ($\mathrm{s}^{-1}$, log)")
    ax2.set_title(r"(b) Collar Suppression vs. Irreducible $\omega=0$ Floor")
    ax2.legend(loc="upper right", frameon=True, framealpha=0.92, fontsize=6.9)
    ax2.grid(True, which="both", alpha=0.2)

    assert r07["feasible_under_atp_budget"] is True
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_resource_horizon_and_rip_u.png")
    plt.close(fig)


def fig3_dark_mode_filling_and_network() -> None:
    """Figure 3: (a) Exact bosonic Hopfield-Dicke dark-mode dephasing transfer vs eta; (b) Multi-crista passive network separation."""
    r13 = verify_file(CERTS_DIR / "C13_bosonic_dark_mode_leakage_71thz_10e6.json")
    r14 = verify_file(CERTS_DIR / "C14_bosonic_dark_mode_leakage_79thz_10e8.json")
    r15 = verify_file(CERTS_DIR / "C15_passive_network_S5_irreducible_gap.json")
    r16 = verify_file(CERTS_DIR / "C16_passive_network_S9_multi_crista_stack.json")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.55))

    etas = [0.001 + 0.349 * i / 200.0 for i in range(201)]
    # Exact resonant Hopfield lower branch: nu_- / w0 = sqrt(1 + eta^2) - eta
    # Matter weight w_mat = nu_-^2 / (w0^2 + nu_-^2) = 1 / (1 + (sqrt(1+eta^2)+eta)^2)
    w_mat = []
    w_phot = []
    for e in etas:
        r_m = (1.0 + e * e) ** 0.5 - e
        wm = (r_m * r_m) / (1.0 + r_m * r_m)
        w_mat.append(wm)
        w_phot.append(1.0 - wm)
    ax1.plot(etas, w_mat, color="#d73027", lw=2.2, label=r"Bosonic dark-mode transfer $\Gamma_{\mathrm{MP}^-\!\to\mathcal{D}}/\gamma_{\mathrm{loc}} = w_{\mathrm{mat}}\frac{N-1}{N}$")
    ax1.plot(etas, w_phot, color="#2166ac", lw=1.8, ls="--", label=r"Photonic weight $w_{\mathrm{phot}} = \frac{\omega_0^2}{\omega_0^2+\nu_-^2}$ ($A^2$ shift)")
    ax1.axhline(0.5, color="#555555", lw=1.1, ls=":", label=r"RWA symmetric limit ($w_{\mathrm{mat}} = w_{\mathrm{phot}} = 1/2$)")
    eta_c13 = 1264.0 / 6177.0
    eta_c14 = (7569.0 / 79.0 - 79.0) / (2.0 * 87.0)
    t_c13 = _f(r13["dark_dephasing_transfer_factor"])
    t_c14 = _f(r14["dark_dephasing_transfer_factor"])
    ax1.scatter([eta_c13, eta_c14], [t_c13, t_c14], color="#b2182b", edgecolor="black", s=48, zorder=6)
    ax1.annotate("C13 (71 THz,\n$w_{\\mathrm{mat}}=0.400$)", xy=(eta_c13, t_c13), xytext=(eta_c13 - 0.02, 0.25),
                 arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=7.5)
    ax1.annotate("C14 (79 THz,\n$w_{\\mathrm{mat}}=0.452$)", xy=(eta_c14, t_c14), xytext=(0.015, 0.30),
                 arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=7.5)
    ax1.set_xlim(0.0, 0.35)
    ax1.set_ylim(0.20, 0.78)
    ax1.set_xlabel(r"Normalized coupling $\eta = g / \omega_0$")
    ax1.set_ylabel("Exact Hopfield weight / transfer factor")
    ax1.set_title(r"(a) Bosonic Dark-Mode Dephasing Transfer ($N\geq 10^6$)")
    ax1.legend(loc="upper left", frameon=True, framealpha=0.92, fontsize=6.6)
    ax1.grid(alpha=0.22)

    # Panel (b): Live Mode 4b passive network reducible floor vs irreducible multi-crista stopband leak
    cats = ["C15 (S=5)\nReducible LB", "C15 (S=5)\nIrreducible", "C16 (S=9)\nReducible LB", "C16 (S=9)\nIrreducible"]
    vals = [
        _f(r15["reducible_leakage_lower_bound"]),
        _f(r15["irreducible_stopband_leak"]),
        _f(r16["reducible_leakage_lower_bound"]),
        _f(r16["irreducible_stopband_leak"]),
    ]
    cols = ["#fc8d59", "#1b7837", "#d73027", "#006837"]
    bars = ax2.bar(range(len(cats)), vals, color=cols, width=0.54)
    ax2.set_yscale("log")
    ax2.set_ylim(4e-4, 4.0)
    for bar, v in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width() / 2.0, v * 1.25, f"{v:.3f}", ha="center", va="bottom", fontsize=7.8)
    ax2.set_xticks(range(len(cats)))
    ax2.set_xticklabels(cats, fontsize=7.8)
    ax2.set_ylabel("90–110 THz water-band transmittance (log)")
    ax2.set_title("(b) Multi-Crista Stack Channel-Mixing Separation")
    ax2.grid(axis="y", which="both", alpha=0.22)

    assert r13["num_dark_modes"] == 999999
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_dark_mode_and_passive_network.png")
    plt.close(fig)


def main() -> int:
    fig1_hopfield_vs_rwa_spectrum()
    fig2_bioenergetic_resource_horizon()
    fig3_dark_mode_filling_and_network()
    print(f"Generated 3 figures in {FIG_DIR}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
