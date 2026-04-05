#!/usr/bin/env python3
"""
Rincoin Baseline Supply Dynamics (Fully Parameterized Deterministic Model)
==========================================================================

Generates the deterministic macroeconomic baseline scenario (2025-2800).
Demonstrates the convergence of the Real Circulating Supply under constant
entropic loss, assuming a standard Satoshi Nakamoto-style halving schedule
transitioning to a fixed reward.

This script serves as the **reference benchmark** against which the
customized halving scenarios and Proof of Rinne regenerative models are
compared. It computes the exact piecewise integrals for the halving epochs,
the fixed emission phase, and the post-mining decay phase.

This script is fully automated. By configuring the ``SCENARIOS`` dictionary,
it handles the complete computation and high-fidelity plotting pipeline.

Paper Figures
-------------
- Figure 1 — Baseline Standard: output/fig_baseline_deterministic.png

Usage
-----
    python src/deterministic/baseline_supply_dynamics.py
"""

import math
import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker  # noqa: F401 – available for future axis tweaks


# ==========================================
# 1. System Parameters & Scenario Definitions
# ==========================================

BLOCKS_PER_YEAR = 525_600   # 1 block per minute
MAX_SUPPLY = 168_000_000    # Absolute maximum supply (Macro-hard cap)
START_YEAR = 2025
SIMULATION_YEARS = 775      # Horizon up to year 2800

SCENARIOS: dict[str, dict] = {
    "Baseline_Standard": {
        "title": "Rincoin Supply Over Time in the Baseline Scenario (2025~2800)",
        "loss_rate": 0.01,              # 1% entropic loss per annum
        "final_reward": 0.4,            # Fixed reward after halvings
        "halvings_before_fixed": 7,
        "initial_reward": 50,
        "blocks_per_epoch": 210_000,
        "supply_label": "B",
        "milestone_label": "Seventh Halving => Fixed Reward",
    },
}


# ==========================================
# 2. Simulation Engine
# ==========================================

def compute_baseline_trajectories(
    loss_rate: float,
    final_reward: float,
    halvings: int,
    r0: float,
    blocks_per_epoch: int,
    max_supply: float,
    sim_years: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    """
    Compute the deterministic supply trajectory for standard halvings.

    Returns
    -------
    t_array : ndarray — Relative time axis (years from genesis)
    S_arr   : ndarray — Total mined supply S(t)
    C_arr   : ndarray — Real circulating supply C(t) after entropic decay
    t_fix   : float   — Year when halving schedule ends (fixed-reward onset)
    t_trans : float   — Year when macro-hard cap is reached (mining ends)
    """
    D = 1.0 - loss_rate
    gamma = -math.log(D)
    r_fix = BLOCKS_PER_YEAR * final_reward
    stabilizer_fix = r_fix / gamma

    # Halving interval in years
    T = blocks_per_epoch / BLOCKS_PER_YEAR
    t_fix = halvings * T

    # Cumulative supply at t_fix
    S_fix = sum(blocks_per_epoch * r0 * (0.5 ** i) for i in range(halvings))
    t_trans = t_fix + (max_supply - S_fix) / r_fix

    # Real circulating supply at t_fix (midpoint-decay approximation)
    C_fix_computed = sum(
        blocks_per_epoch * r0 * (0.5 ** i) * (D ** (t_fix - T * (i + 0.5)))
        for i in range(halvings)
    )

    # Peak circulating supply at mining end
    C_peak = (
        C_fix_computed * math.exp(-gamma * (t_trans - t_fix))
        + stabilizer_fix * (1 - math.exp(-gamma * (t_trans - t_fix)))
    )

    t_array = np.linspace(0, sim_years, sim_years)
    S_arr = np.zeros_like(t_array)
    C_arr = np.zeros_like(t_array)

    for i, t_val in enumerate(t_array):
        if t_val == 0:
            continue

        # --- Total Supply S(t) ---
        if t_val < t_fix:
            k = int(t_val / T)
            sum_supply = sum(
                blocks_per_epoch * r0 * (0.5 ** j) for j in range(k)
            )
            rem_years = t_val - T * k
            S_arr[i] = sum_supply + rem_years * BLOCKS_PER_YEAR * r0 * (0.5 ** k)
        elif t_fix <= t_val < t_trans:
            S_arr[i] = S_fix + BLOCKS_PER_YEAR * (t_val - t_fix) * final_reward
        else:
            S_arr[i] = max_supply

        # --- Real Circulating Supply C(t) ---
        if t_val < t_fix:
            k = int(t_val / T)
            sum_c = sum(
                blocks_per_epoch * r0 * (0.5 ** j) * (D ** (t_val - T * (j + 0.5)))
                for j in range(k)
            )
            rem_years = t_val - T * k
            if rem_years > 0:
                r_k = BLOCKS_PER_YEAR * r0 * (0.5 ** k)
                sum_c += (r_k / gamma) * (1 - math.exp(-gamma * rem_years))
            C_arr[i] = sum_c
        elif t_fix <= t_val < t_trans:
            exp_neg = math.exp(-gamma * (t_val - t_fix))
            C_arr[i] = C_fix_computed * exp_neg + stabilizer_fix * (1 - exp_neg)
        else:
            exp_neg = math.exp(-gamma * (t_val - t_trans))
            C_arr[i] = C_peak * exp_neg

    return t_array, S_arr, C_arr, t_fix, t_trans


# ==========================================
# 3. Execution & Automated Plotting
# ==========================================

def main() -> None:
    os.makedirs("output", exist_ok=True)

    for scenario_id, config in SCENARIOS.items():
        print(f"Processing {scenario_id}...")

        t_array, S_arr, C_arr, t_fix, t_trans = compute_baseline_trajectories(
            config["loss_rate"],
            config["final_reward"],
            config["halvings_before_fixed"],
            config["initial_reward"],
            config["blocks_per_epoch"],
            MAX_SUPPLY,
            SIMULATION_YEARS,
        )

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        lbl_s = config["supply_label"]
        loss_pct = config["loss_rate"] * 100

        # Plot trajectories
        ax.plot(
            t_array, S_arr,
            label=f"Total Supply $S_{lbl_s}(t)$",
            color="#1565c0", lw=2,
        )
        ax.plot(
            t_array, C_arr,
            label=f"Real Circulating Supply ({loss_pct:.0f}% loss per annum) $C_{lbl_s}(t)$",
            color="#ef6c00", lw=2,
        )

        # Architectural milestones
        ax.axvline(
            x=t_fix, color="gray", linestyle="--", alpha=0.8,
            label=(
                f"{config['milestone_label']} {config['final_reward']} RIN/Block"
                f" ($t_{{fix}}$ = {t_fix:.2f})"
            ),
        )
        ax.axvline(
            x=t_trans, color="#c62828", linestyle="--", alpha=0.8,
            label=f"Mining End ($t_{{trans}}$ = {t_trans:.2f})",
        )
        ax.axhline(
            y=MAX_SUPPLY, color="#2e7d32", linestyle="--", alpha=0.8,
            label=f"Maximum Supply ({MAX_SUPPLY / 1e6:.0f}M RIN)",
        )

        # Dynamic X-axis (2025, 2100, 2150, ... 2800)
        actual_years = [2025] + list(
            np.arange(2100, START_YEAR + SIMULATION_YEARS + 1, 50)
        )
        x_ticks_values = [year - START_YEAR for year in actual_years]
        ax.set_xticks(x_ticks_values)
        ax.set_xticklabels([str(year) for year in actual_years])

        # Dynamic Y-axis
        _, y_max = ax.get_ylim()
        step = 25_000_000
        yticks = np.concatenate((
            [0, 21_000_000, 35_000_000, 50_000_000],
            np.arange(75_000_000, y_max + step, step),
        ))

        for val in [MAX_SUPPLY, 10_500_000, 21_000_000]:
            if val not in yticks:
                yticks = np.append(yticks, val)

        yticks = np.sort(yticks)
        yticklabels = [
            f"{tick / 1e6:.1f}M" if tick in [10_500_000, 21_000_000]
            else f"{int(tick / 1e6)}M"
            for tick in yticks
        ]

        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)

        for label in ax.get_yticklabels():
            text_val = label.get_text()
            if text_val == f"{int(MAX_SUPPLY / 1e6)}M":
                label.set_color("#2e7d32")
                label.set_fontweight("bold")
            elif text_val == "10.5M":
                label.set_color("gray")

        # Formatting
        ax.set_xlabel("Years", fontsize=12)
        ax.set_ylabel("Rincoin Supply (RIN)", fontsize=12)
        ax.set_title(config["title"], fontsize=14, pad=15, fontweight="bold")
        ax.legend(loc="best", framealpha=0.9, fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.7)
        plt.tight_layout()

        output_filename = "output/fig_baseline_deterministic.png"
        plt.savefig(output_filename, dpi=300, bbox_inches="tight")
        plt.close()

    print(
        "Baseline deterministic scenario successfully generated"
        " and saved to output/ directory."
    )


if __name__ == "__main__":
    main()
