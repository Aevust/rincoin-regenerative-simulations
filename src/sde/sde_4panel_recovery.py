#!/usr/bin/env python3
"""
Rincoin 4-Panel ZKP Recovery Model (Micro / Macro Comparison)
=============================================================

Simulates macroeconomic homeostasis via the Recirculation Incentive Mechanism
and ZKP Owner Recovery, rendering a 4-panel grid comparing:

- Top-Left:     (A) No Recovery — Single simulation (microscopic epoch shocks)
- Top-Right:    (B) 10% ZKP Recovery — Single simulation
- Bottom-Left:  (A) No Recovery — Median of N simulations (macroscopic)
- Bottom-Right: (B) 10% ZKP Recovery — Median of N simulations

This script is fully parameterized: adjustments to MU, INITIAL_SUPPLY, or
TARGET_SUPPLY will dynamically update all panels, titles, and reference lines.

Paper Figures
-------------
- [Figure 12] INITIAL_SUPPLY=21_000_000 / MU=0.015
- [Figure 13] INITIAL_SUPPLY=21_000_000 / MU=0.016
- [Figure 14] INITIAL_SUPPLY=21_000_000 / MU=0.017

Usage
-----
    python src/sde/sde_4panel_recovery.py
"""

import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OUTPUT_DIR = _REPO_ROOT / "output"


# ==========================================
# 1. Simulation Engine
# ==========================================

def simulate_sweeper_v4(
    years: int,
    initial_supply: float,
    rf: float,
    mu: float,
    sigma_c: float,
    epoch_mean: float,
    epoch_std: float,
    beta: float,
    recovery_mu: float,
    recovery_sigma: float,
    num_sims: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Execute a vectorized Monte Carlo simulation integrating continuous SDE
    decay with discrete epoch sweeping and ZKP recovery.

    Returns
    -------
    t_array  : ndarray — Time axis
    C_matrix : ndarray — Active Circulating Supply
    D_matrix : ndarray — Dormant Vulnerable Supply
    V_matrix : ndarray — Shielded Vault Supply (Permanently Locked)
    """
    dt = 1
    t_array = np.arange(0, years + dt, dt)
    num_steps = len(t_array)

    C_matrix = np.zeros((num_sims, num_steps))
    D_matrix = np.zeros((num_sims, num_steps))
    V_matrix = np.zeros((num_sims, num_steps))
    C_matrix[:, 0] = initial_supply

    next_sweep_timer = np.maximum(
        10, np.random.normal(epoch_mean, epoch_std, num_sims)
    )

    Z_loss = np.random.normal(0, 1, (num_sims, num_steps))
    Z_rec = (
        np.random.normal(0, 1, (num_sims, num_steps))
        if (recovery_mu > 0 or recovery_sigma > 0)
        else np.zeros((num_sims, num_steps))
    )

    for i in range(1, num_steps):
        current_mu = np.maximum(0, mu + sigma_c * Z_loss[:, i])
        loss = C_matrix[:, i - 1] * current_mu

        next_sweep_timer -= dt
        sweep_mask = next_sweep_timer <= 0

        sweep_amount = np.zeros(num_sims)
        bounty = np.zeros(num_sims)
        recovered = np.zeros(num_sims)
        locked = np.zeros(num_sims)

        if np.any(sweep_mask):
            sweep_amount[sweep_mask] = (
                D_matrix[:, i - 1][sweep_mask] + loss[sweep_mask]
            )
            bounty[sweep_mask] = sweep_amount[sweep_mask] * beta
            to_vault = sweep_amount[sweep_mask] * (1.0 - beta)

            gamma_i = (
                np.clip(
                    recovery_mu + recovery_sigma * Z_rec[sweep_mask, i],
                    0.0, 1.0,
                )
                if (recovery_mu > 0 or recovery_sigma > 0)
                else np.zeros(np.sum(sweep_mask))
            )

            recovered[sweep_mask] = to_vault * gamma_i
            locked[sweep_mask] = to_vault - recovered[sweep_mask]

            num_swept = np.sum(sweep_mask)
            next_sweep_timer[sweep_mask] = np.maximum(
                10, np.random.normal(epoch_mean, epoch_std, num_swept)
            )

        C_matrix[:, i] = C_matrix[:, i - 1] + rf - loss + bounty + recovered
        D_matrix[:, i] = D_matrix[:, i - 1] + loss - sweep_amount
        V_matrix[:, i] = V_matrix[:, i - 1] + locked

    return t_array, C_matrix, D_matrix, V_matrix


# ==========================================
# 2. System Parameters
# ==========================================

YEARS = 400
INITIAL_SUPPLY = 21_000_000   # Adjust: 21M or 28M
TARGET_SUPPLY = 21_000_000
RF = 315_360
MU = 0.015                    # Adjust: 0.015, 0.016, 0.017
SIGMA_C = 0.005
SWEEP_MEAN = 30
SWEEP_STD = 10
BETA = 0.02
NUM_SIMS = 1000


# ==========================================
# 3. Main Execution
# ==========================================

def main() -> None:
    common = dict(
        years=YEARS, initial_supply=INITIAL_SUPPLY, rf=RF, mu=MU,
        sigma_c=SIGMA_C, epoch_mean=SWEEP_MEAN, epoch_std=SWEEP_STD,
        beta=BETA, num_sims=NUM_SIMS,
    )

    np.random.seed(42)
    t_array, C_A, D_A, V_A = simulate_sweeper_v4(
        **common, recovery_mu=0.0, recovery_sigma=0.0,
    )

    np.random.seed(42)
    t_array, C_B, D_B, V_B = simulate_sweeper_v4(
        **common, recovery_mu=0.10, recovery_sigma=0.05,
    )

    eq_A = RF / (MU * (1 - BETA))

    # ---- 4-Panel Grid ----
    fig, axes = plt.subplots(
        2, 2, figsize=(18, 13),
        gridspec_kw={"hspace": 0.38, "wspace": 0.28}, dpi=100,
    )

    sim_idx = 0
    COL_A = "#c62828"
    COL_B = "#1565c0"

    init_m = INITIAL_SUPPLY / 1e6
    target_m = TARGET_SUPPLY / 1e6

    # Top-Left: (A) No Recovery — Single Sim
    ax = axes[0][0]
    ax.plot(t_array, C_A[sim_idx] / 1e6, color=COL_A, lw=1.5, label="C (Circulating)")
    ax.plot(t_array, D_A[sim_idx] / 1e6, color="#78909c", lw=1.2, alpha=0.7, label="D (Dormant)")
    ax.plot(t_array, V_A[sim_idx] / 1e6, color="#6a1b9a", lw=1.5, alpha=0.8, label="V (Vault, permanent)")
    ax.axhline(y=eq_A / 1e6, color="green", ls="--", lw=1.5, label=f"Eq. ({eq_A/1e6:.2f}M)")
    ax.set_title(
        rf"(A) No Recovery: Single Sim: Base Loss $\boldsymbol{{\mu={MU*100:.1f}\%}}$ [Init: {init_m:.1f}M]"
        + "\nV accumulates permanently; C trends to equilibrium",
        fontsize=14, color=COL_A, fontweight="bold",
    )
    ax.set_ylabel("Supply (M RIN)", fontsize=12)
    ax.legend(fontsize=10, loc="center left")
    ax.grid(True, ls=":", alpha=0.4)

    # Top-Right: (B) 10% ZKP Recovery — Single Sim
    ax = axes[0][1]
    ax.plot(t_array, C_B[sim_idx] / 1e6, color=COL_B, lw=1.5, label="C (Circulating)")
    ax.plot(t_array, D_B[sim_idx] / 1e6, color="#78909c", lw=1.2, alpha=0.7, label="D (Dormant)")
    ax.plot(t_array, V_B[sim_idx] / 1e6, color="#6a1b9a", lw=1.5, alpha=0.8, label="V (Vault, permanent)")
    ax.axhline(y=target_m, color="gray", ls="--", lw=1, alpha=0.5, label=f"{target_m:.0f}M Target")
    ax.set_title(
        rf"(B) One-Time 10% Recovery: Single Sim: Base Loss $\boldsymbol{{\mu={MU*100:.1f}\%}}$ [Init: {init_m:.1f}M]"
        + "\nRecovery events act as discrete shocks; V still dominates",
        fontsize=14, color=COL_B, fontweight="bold",
    )
    ax.set_ylabel("Supply (M RIN)", fontsize=12)
    ax.legend(fontsize=10, loc="center left")
    ax.grid(True, ls=":", alpha=0.4)

    # Bottom-Left: (A) No Recovery — Median of N Sims
    ax = axes[1][0]
    med_A = np.median(C_A, axis=0)
    for i in range(30):
        ax.plot(t_array, C_A[i] / 1e6, color="gray", alpha=0.06, lw=0.5)
    ax.fill_between(
        t_array,
        np.percentile(C_A, 2.5, axis=0) / 1e6,
        np.percentile(C_A, 97.5, axis=0) / 1e6,
        color="#ef9a9a", alpha=0.25, label="95% CI",
    )
    ax.plot(t_array, med_A / 1e6, color=COL_A, lw=2.5, label="Median C")
    ax.plot(t_array, np.median(V_A, axis=0) / 1e6, color="#6a1b9a", lw=1.5, ls="--", label="Median V")
    ax.axhline(y=eq_A / 1e6, color="green", ls="--", lw=1.5, label=f"Eq. ({eq_A/1e6:.2f}M)")
    ax.set_title(
        rf"(A) No Recovery: Median of {NUM_SIMS} sims: Base Loss $\boldsymbol{{\mu={MU*100:.1f}\%}}$ [Init: {init_m:.1f}M]",
        fontsize=14, color=COL_A, fontweight="bold",
    )
    ax.set_xlabel("Years", fontsize=12)
    ax.set_ylabel("Supply (M RIN)", fontsize=12)
    ax.legend(fontsize=10, loc="center left")
    ax.grid(True, ls=":", alpha=0.4)

    # Bottom-Right: (B) 10% ZKP Recovery — Median of N Sims
    ax = axes[1][1]
    med_B = np.median(C_B, axis=0)
    for i in range(30):
        ax.plot(t_array, C_B[i] / 1e6, color="gray", alpha=0.06, lw=0.5)
    ax.fill_between(
        t_array,
        np.percentile(C_B, 2.5, axis=0) / 1e6,
        np.percentile(C_B, 97.5, axis=0) / 1e6,
        color="#90caf9", alpha=0.25, label="95% CI",
    )
    ax.plot(t_array, med_B / 1e6, color=COL_B, lw=2.5, label="Median C")
    ax.plot(t_array, np.median(V_B, axis=0) / 1e6, color="#6a1b9a", lw=1.5, ls="--", label="Median V")
    ax.axhline(y=target_m, color="gray", ls="--", lw=1, alpha=0.5, label=f"{target_m:.0f}M Target")
    ax.set_title(
        rf"(B) One-Time 10% Recovery: Median of {NUM_SIMS} sims: Base Loss $\boldsymbol{{\mu={MU*100:.1f}\%}}$ [Init: {init_m:.1f}M]"
        + "\nHuman intervention elegantly counterbalances extreme entropy",
        fontsize=14, color=COL_B, fontweight="bold",
    )
    ax.set_xlabel("Years", fontsize=12)
    ax.set_ylabel("Supply (M RIN)", fontsize=12)
    ax.legend(fontsize=10, loc="upper left")
    ax.grid(True, ls=":", alpha=0.4)

    _OUTPUT_DIR.mkdir(exist_ok=True)
    plt.savefig(
        _OUTPUT_DIR / f"fig_4panel_recovery_mu{MU * 100:.1f}.png",
        dpi=300, bbox_inches="tight",
    )
    plt.show()


if __name__ == "__main__":
    main()
