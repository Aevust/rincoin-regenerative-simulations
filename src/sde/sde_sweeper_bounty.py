#!/usr/bin/env python3
"""
Rincoin Cryptographic Epoch Sweeper Model (Bounty Only)
=======================================================

Simulates macroeconomic homeostasis via the Recirculation Incentive Mechanism.
Integrates discrete, event-driven epoch shocks (Sweeper Gold Rush) into the
continuous SDE model.

This script is fully automated: adjustments to initial supplies, target
supplies, or entropic loss rates (mu) will dynamically update all simulations,
target lines, and chart titles.

Paper Figures
-------------
- [Figure 9] Dual-panel: INITIAL_SUPPLY=21_000_000 / MU_1=0.015, MU_2=0.016

Usage
-----
    python src/sde/sde_sweeper_bounty.py
"""

import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# ==========================================
# 1. Simulation Engine
# ==========================================

def simulate_event_sweeper_model(
    years: int,
    initial_supply: float,
    annual_issuance: float,
    mu: float,
    sigma: float,
    epoch_mean: float,
    epoch_std: float,
    beta: float,
    num_sims: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Execute a vectorized Monte Carlo simulation integrating continuous SDE
    decay with discrete epoch sweeping events (Sweeper Bounty only).

    Returns
    -------
    t_array : ndarray
    C_matrix : ndarray  — Active Circulating Supply
    D_matrix : ndarray  — Dormant Vulnerable Supply (Pending Sweep)
    """
    dt = 1
    t_array = np.arange(0, years + dt, dt)
    num_steps = len(t_array)

    C_matrix = np.zeros((num_sims, num_steps))
    D_matrix = np.zeros((num_sims, num_steps))
    C_matrix[:, 0] = initial_supply

    next_sweep_timer = np.maximum(
        10, np.random.normal(epoch_mean, epoch_std, num_sims)
    )
    Z = np.random.normal(0, 1, (num_sims, num_steps))

    for i in range(1, num_steps):
        current_mu = np.maximum(0, mu + sigma * Z[:, i])
        loss = C_matrix[:, i - 1] * current_mu

        next_sweep_timer -= dt
        sweep_mask = next_sweep_timer <= 0

        sweep_amount = np.zeros(num_sims)
        sweep_amount[sweep_mask] = D_matrix[:, i - 1][sweep_mask] + loss[sweep_mask]

        num_swept = np.sum(sweep_mask)
        if num_swept > 0:
            next_sweep_timer[sweep_mask] = np.maximum(
                10, np.random.normal(epoch_mean, epoch_std, num_swept)
            )

        bounty = sweep_amount * beta

        C_matrix[:, i] = C_matrix[:, i - 1] + annual_issuance - loss + bounty
        D_matrix[:, i] = D_matrix[:, i - 1] + loss - sweep_amount

    return t_array, C_matrix, D_matrix


# ==========================================
# 2. System Parameters
# ==========================================

YEARS = 400
INITIAL_SUPPLY = 21_000_000
TARGET_SUPPLY = 21_000_000
ANNUAL_ISSUANCE = 315_360
LOSS_VOLATILITY = 0.005
EPOCH_MEAN = 30
EPOCH_STD = 10
BOUNTY_BETA = 0.02
NUM_SIMULATIONS = 1000

MU_1 = 0.015  # Top panel
MU_2 = 0.016  # Bottom panel


# ==========================================
# 3. Main Execution
# ==========================================

def main() -> None:
    t_array, C_top, _ = simulate_event_sweeper_model(
        YEARS, INITIAL_SUPPLY, ANNUAL_ISSUANCE, MU_1,
        LOSS_VOLATILITY, EPOCH_MEAN, EPOCH_STD, BOUNTY_BETA, NUM_SIMULATIONS,
    )
    t_array, C_bot, _ = simulate_event_sweeper_model(
        YEARS, INITIAL_SUPPLY, ANNUAL_ISSUANCE, MU_2,
        LOSS_VOLATILITY, EPOCH_MEAN, EPOCH_STD, BOUNTY_BETA, NUM_SIMULATIONS,
    )

    def calc_stats(C):
        return (
            np.median(C, axis=0),
            np.percentile(C, 2.5, axis=0),
            np.percentile(C, 97.5, axis=0),
        )

    med_top, lb_top, ub_top = calc_stats(C_top)
    med_bot, lb_bot, ub_bot = calc_stats(C_bot)

    target_top = ANNUAL_ISSUANCE / (MU_1 * (1 - BOUNTY_BETA))
    target_bot = ANNUAL_ISSUANCE / (MU_2 * (1 - BOUNTY_BETA))

    # Plotting
    fig, axes = plt.subplots(2, 1, figsize=(12, 12))
    formatter = ticker.FuncFormatter(lambda x, pos: f"{x * 1e-6:,.1f}M")

    init_m = INITIAL_SUPPLY / 1e6
    target_m = TARGET_SUPPLY / 1e6

    for ax, C_data, med, lb, ub, mu_val, eq_val in [
        (axes[0], C_top, med_top, lb_top, ub_top, MU_1, target_top),
        (axes[1], C_bot, med_bot, lb_bot, ub_bot, MU_2, target_bot),
    ]:
        for i in range(50):
            ax.plot(t_array, C_data[i], color="gray", alpha=0.1, linewidth=0.5)
        ax.fill_between(
            t_array, lb, ub, color="orange", alpha=0.3, label="95% Confidence Interval",
        )
        ax.plot(t_array, med, color="darkorange", linewidth=2, label="Median Expected Supply")
        ax.axhline(
            y=TARGET_SUPPLY, color="red", linestyle=":", linewidth=1.5,
            label=f"Target ({target_m:.0f}M RIN)",
        )
        ax.axhline(
            y=eq_val, color="green", linestyle="--", linewidth=2,
            label=f"New Equilibrium (Avg) (~{eq_val/1e6:.2f}M)",
        )

        ax.set_title(
            r"Macroeconomic Homeostasis via the Recirculation Incentive Mechanism"
            + "\n"
            + r"Baseline Thermodynamic Equilibrium (Sweeper Bounty Only)"
            + "\n"
            + rf"Base Loss $\mu={mu_val*100:.1f}\%$ / Epoch $\sim \mathcal{{N}}({EPOCH_MEAN}, {EPOCH_STD}^2)$ Years"
            + rf" / Monte Carlo (N={NUM_SIMULATIONS}) / [Init: {init_m:.1f}M] / Bounty $\beta={BOUNTY_BETA*100:.1f}\%$",
            fontsize=14, pad=10,
        )
        ax.set_ylabel("Circulating Supply (RIN)", fontsize=12)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.7)
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1_000_000))
        ax.yaxis.set_major_formatter(formatter)

    axes[1].set_xlabel("Years", fontsize=12)
    plt.tight_layout()

    os.makedirs("output", exist_ok=True)
    plt.savefig(
        "output/fig_sweeper_bounty_dual_panel.png",
        dpi=300, bbox_inches="tight",
    )
    plt.show()


if __name__ == "__main__":
    main()
