#!/usr/bin/env python3
"""
Rincoin Stochastic Supply Simulation (Fully Parameterized SDE Model)
====================================================================

Simulates the macroeconomic homeostasis of the Rincoin circulating supply
using a highly optimized, vectorized Monte Carlo method based on the
Euler-Maruyama discretization:

    dC_t = r_f dt - C_t (mu dt + sigma dW_t)

This script is fully automated: adjustments to BASE_LOSS_RATE, INITIAL_SUPPLY,
or TARGET_SUPPLY will dynamically update all simulations, statistical bounds,
target lines, and chart titles without requiring manual string edits.

Paper Figures
-------------
- [Figure 6]  Baseline:   INITIAL_SUPPLY=21_000_000 / BASE_LOSS_RATE=0.015
- [Figure 7]  Baseline:   INITIAL_SUPPLY=21_000_000 / BASE_LOSS_RATE=0.016
- [Figure 8]  Oversupply: INITIAL_SUPPLY=28_000_000 / BASE_LOSS_RATE=0.015
- [Figure 10] Oversupply: INITIAL_SUPPLY=28_000_000 / BASE_LOSS_RATE=0.016

Usage
-----
    python src/sde/sde_baseline.py
"""

import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# ==========================================
# 1. Simulation Engine
# ==========================================

def simulate_stochastic_supply(
    years: int,
    initial_supply: float,
    annual_issuance: float,
    base_loss_rate: float,
    loss_volatility: float,
    num_simulations: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Execute a fully vectorized Monte Carlo simulation of the Rincoin supply SDE.

    Parameters
    ----------
    years : int
        Simulation horizon in years.
    initial_supply : float
        Initial circulating supply C(0).
    annual_issuance : float
        Deterministic annual issuance r_f (RIN/year).
    base_loss_rate : float
        Mean entropic loss rate mu.
    loss_volatility : float
        Volatility of the stochastic loss rate sigma.
    num_simulations : int
        Number of Monte Carlo paths (N).

    Returns
    -------
    t_array : ndarray, shape (num_steps,)
        Time axis in years.
    supplies : ndarray, shape (num_simulations, num_steps)
        Simulated circulating supply paths.
    """
    dt = 1  # 1-year time step
    t_array = np.arange(0, years + dt, dt)
    num_steps = len(t_array)

    supplies = np.zeros((num_simulations, num_steps))
    supplies[:, 0] = initial_supply

    # Pre-generate standard normal random variables for the Wiener process
    Z = np.random.normal(0, 1, (num_simulations, num_steps))

    # Vectorized Euler-Maruyama Method
    for i in range(1, num_steps):
        stochastic_loss_rate = np.maximum(
            0, base_loss_rate + loss_volatility * Z[:, i]
        )
        loss_amount = supplies[:, i - 1] * stochastic_loss_rate
        supplies[:, i] = supplies[:, i - 1] + annual_issuance - loss_amount

    return t_array, supplies


# ==========================================
# 2. System Parameters & Simulation Setup
# ==========================================

YEARS = 400
INITIAL_SUPPLY = 21_000_000   # Adjust: 21_000_000 (baseline) or 28_000_000 (oversupply)
TARGET_SUPPLY = 21_000_000    # Satoshi Nakamoto Target (reference line)
ANNUAL_ISSUANCE = 315_360     # r_f = 0.6 RIN/block * 525,600 blocks
BASE_LOSS_RATE = 0.015        # Adjust: 0.015, 0.016, 0.017, etc.
LOSS_VOLATILITY = 0.005       # Stochastic volatility sigma (0.5%)
NUM_SIMULATIONS = 1000        # Monte Carlo paths (N)


# ==========================================
# 3. Main Execution
# ==========================================

def main() -> None:
    t_array, all_supplies = simulate_stochastic_supply(
        YEARS, INITIAL_SUPPLY, ANNUAL_ISSUANCE,
        BASE_LOSS_RATE, LOSS_VOLATILITY, NUM_SIMULATIONS,
    )

    # Statistical computations
    median_supply = np.median(all_supplies, axis=0)
    lower_bound = np.percentile(all_supplies, 2.5, axis=0)
    upper_bound = np.percentile(all_supplies, 97.5, axis=0)

    # Plotting
    plt.figure(figsize=(12, 7))

    init_m = INITIAL_SUPPLY / 1e6
    target_m = TARGET_SUPPLY / 1e6

    for i in range(50):
        plt.plot(t_array, all_supplies[i], color="gray", alpha=0.1, linewidth=0.5)

    plt.fill_between(
        t_array, lower_bound, upper_bound,
        color="orange", alpha=0.3, label="95% Confidence Interval",
    )
    plt.plot(
        t_array, median_supply,
        color="darkorange", linewidth=2, label="Median Expected Supply",
    )
    plt.axhline(
        y=TARGET_SUPPLY, color="red", linestyle="--", linewidth=1.5, alpha=0.8,
        label=f"Target Equilibrium ({target_m:.0f}M RIN)",
    )

    plt.title(
        rf"Rincoin Phase Transition: Stochastic Simulation ({YEARS} Years)"
        + "\n"
        + rf"Monte Carlo Method (N={NUM_SIMULATIONS}) / Base Loss $\mu={BASE_LOSS_RATE*100:.1f}\%$ [Init: {init_m:.1f}M]",
        fontsize=14, pad=15,
    )
    plt.xlabel("Years", fontsize=12)
    plt.ylabel("Circulating Supply (RIN)", fontsize=12)

    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1_000_000))
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f"{x * 1e-6:,.1f}M")
    )

    plt.legend(loc="upper right", framealpha=0.9, fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.7)
    plt.tight_layout()

    os.makedirs("output", exist_ok=True)
    plt.savefig(
        f"output/fig_baseline_{INITIAL_SUPPLY // 1_000_000}m_mu{BASE_LOSS_RATE * 100:.1f}.png",
        dpi=300, bbox_inches="tight",
    )
    plt.show()


if __name__ == "__main__":
    main()
