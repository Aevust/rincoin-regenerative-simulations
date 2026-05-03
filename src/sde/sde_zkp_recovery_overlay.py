#!/usr/bin/env python3
"""
Rincoin ZKP Owner Recovery Model (Nash Equilibrium Proof — High Resolution)
===========================================================================

Simulates macroeconomic homeostasis via the Recirculation Incentive Mechanism
and ZKP Owner Recovery, overlaying baseline (0% recovery) and ZKP (10% recovery)
scenarios on a single plot with theoretical equilibrium lines.

This is the **highlight model** of the paper: at N=100,000 with MU=0.017,
it proves that ZKP Owner Recovery restores the 21M target even under
extreme entropic pressure — "The Miracle of Equilibrium".

This script is fully automated: adjustments to MU, INITIAL_SUPPLY, or
TARGET_SUPPLY will dynamically update all simulations, statistical bounds,
target lines, and chart titles.

Paper Figures
-------------
- [Figure 12 lower] MU=0.015, NUM_SIMS=20_000
- [Figure 13 lower] MU=0.016, NUM_SIMS=20_000
- [Figure 14]        MU=0.017, NUM_SIMS=100_000  ("The Miracle of Equilibrium")

Usage
-----
    python src/sde/sde_zkp_recovery_overlay.py
"""

import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OUTPUT_DIR = _REPO_ROOT / "output"


# ==========================================
# 1. Simulation Engine
# ==========================================

def simulate_sweeper_zkp_model(
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
    decay with discrete epoch sweeping and probabilistic ZKP owner recovery.

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
INITIAL_SUPPLY = 21_000_000       # 21M, or 28M for extreme overshoot scenarios
TARGET_SUPPLY = 21_000_000
RF = 315_360
MU = 0.017                        # The Miracle of Equilibrium: 0.015, 0.016, 0.017, 0.018 or 0.019
SIGMA_C = 0.005
SWEEP_MEAN = 30
SWEEP_STD = 10
BETA = 0.02
NUM_SIMS = 20_000                 # High precision: 20_000 or 100_000


# ==========================================
# 3. Main Execution
# ==========================================

def _check_memory_feasibility(num_sims: int, num_steps: int) -> None:
    """Warn if estimated peak memory exceeds a reasonable threshold."""
    # 5 arrays (C, D, V, Z_loss, Z_rec) x float64 x 2 simulation runs
    estimated_bytes = 5 * 2 * num_sims * num_steps * 8
    estimated_gb = estimated_bytes / (1024 ** 3)
    if estimated_gb > 2.0:
        print(
            f"Warning: NUM_SIMS={num_sims:,} will require approximately "
            f"{estimated_gb:.1f} GB of RAM. "
            "Reduce NUM_SIMS to 20_000 if this exceeds available memory."
        )


def main() -> None:
    _check_memory_feasibility(NUM_SIMS, YEARS + 1)

    common = dict(
        years=YEARS, initial_supply=INITIAL_SUPPLY, rf=RF, mu=MU,
        sigma_c=SIGMA_C, epoch_mean=SWEEP_MEAN, epoch_std=SWEEP_STD,
        beta=BETA, num_sims=NUM_SIMS,
    )

    np.random.seed(42)
    t_array, C_A, _, _ = simulate_sweeper_zkp_model(
        **common, recovery_mu=0.0, recovery_sigma=0.0,
    )

    np.random.seed(42)
    t_array, C_B, _, _ = simulate_sweeper_zkp_model(
        **common, recovery_mu=0.10, recovery_sigma=0.05,
    )

    eq_A = RF / (MU * (1 - BETA))
    eq_B = RF / (MU * (1 - BETA) * (1 - 0.10))

    # ---- Overlay Plot ----
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    COL_A, COL_B = "#c62828", "#1565c0"
    init_m = INITIAL_SUPPLY / 1e6
    target_m = TARGET_SUPPLY / 1e6

    ax.plot(
        t_array, np.median(C_A, axis=0),
        color=COL_A, lw=2.5, label="A: No Owner Recovery (0%)",
    )
    ax.plot(
        t_array, np.median(C_B, axis=0),
        color=COL_B, lw=2.5, label="B: ZKP Owner Recovery (~10%)",
    )

    ax.fill_between(
        t_array,
        np.percentile(C_B, 2.5, axis=0),
        np.percentile(C_B, 97.5, axis=0),
        color="#90caf9", alpha=0.15, label="95% CI (B)",
    )

    ax.axhline(
        y=TARGET_SUPPLY, color="gray", ls=":", lw=1.5, alpha=0.7,
        label=f"Target ({target_m:.0f}M RIN)",
    )
    ax.axhline(
        y=eq_A, color=COL_A, ls="--", lw=1.5,
        label=f"Equilibrium A (~{eq_A/1e6:.2f}M)",
    )
    ax.axhline(
        y=eq_B, color=COL_B, ls="--", lw=1.5,
        label=f"Equilibrium B (~{eq_B/1e6:.2f}M)",
    )

    ax.set_title(
        r"Macroeconomic Homeostasis via the Recirculation Incentive Mechanism"
        + "\n"
        + r"Nash Equilibrium Formation via ZKP Owner Recovery"
        + "\n"
        + rf"Base Loss $\mu={MU*100:.1f}\%$ / Epoch $\sim \mathcal{{N}}({SWEEP_MEAN}, {SWEEP_STD}^2)$ Years"
        + rf" / Monte Carlo (N={NUM_SIMS:,}) / [Init: {init_m:.1f}M] / Bounty $\beta={BETA*100:.1f}\%$",
        fontsize=14, pad=15,
    )
    ax.set_xlabel("Years", fontsize=12)
    ax.set_ylabel("Circulating Supply (RIN)", fontsize=12)

    ax.yaxis.set_major_locator(ticker.MultipleLocator(1_000_000))
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f"{x * 1e-6:,.1f}M")
    )

    # Dynamically determine the optimal legend placement based on thermodynamic parameters.
    # If starting exactly at the 21M target under severe entropic decay (MU >= 0.017),
    # relocate the legend completely outside the plot to avoid overlapping the expanding CI bands.
    if MU >= 0.017 and INITIAL_SUPPLY == 21_000_000:
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=10, framealpha=0.9)
    elif INITIAL_SUPPLY > TARGET_SUPPLY:
        # In extreme oversupply scenarios (e.g., 28M), the curve drops from the top-left,
        # making the 'upper right' quadrant the safest internal space.
        ax.legend(loc="upper right", fontsize=10, framealpha=0.9)
    else:
        # Default internal placement for nominal conditions (MU < 0.017, Initial = 21M).
        ax.legend(loc="upper left", fontsize=10, framealpha=0.9)

    ax.grid(True, ls=":", alpha=0.4)

    # Apply tight_layout to ensure the external legend is not cropped during export.
    plt.tight_layout()

    _OUTPUT_DIR.mkdir(exist_ok=True)
    plt.savefig(
        _OUTPUT_DIR / f"fig_zkp_overlay_mu{MU * 100:.1f}.png",
        dpi=300, bbox_inches="tight",
    )
    plt.show()


if __name__ == "__main__":
    main()
