#!/usr/bin/env python3
"""
Rincoin Customized Halving Scenarios (Fully Parameterized Deterministic Model)
==============================================================================

Generates the deterministic macroeconomic supply trajectories (2025-2800) for
various customized halving schedules and entropic loss rates.

This script evaluates three distinct scenarios:
  - Scenario I:   1.3% loss, 0.5 RIN final reward
  - Scenario II:  1.5% loss, 0.6 RIN final reward (Baseline Protocol)
  - Scenario III: 1.5% loss, 0.6 RIN final reward with an extended 1 RIN phase

It is fully automated: adding a new scenario to the ``SCENARIOS`` dictionary
will dynamically compute the exact supply states, map the time horizon,
format the axes, and save the resulting high-fidelity plot to the output
directory.

Paper Figures
-------------
- Scenario I:   output/fig_customized_halving_scenario_i.png
- Scenario II:  output/fig_customized_halving_scenario_ii.png
- Scenario III: output/fig_customized_halving_scenario_iii.png

Usage
-----
    python src/deterministic/customized_halving_scenarios.py
"""

import math
import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker  # noqa: F401 – available for future axis tweaks

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OUTPUT_DIR = _REPO_ROOT / "output"


# ==========================================
# 1. System Parameters & Scenario Definitions
# ==========================================

BLOCKS_PER_YEAR = 525_600   # 1 block per minute
MAX_SUPPLY = 168_000_000    # Absolute maximum supply (Macro-hard cap)
START_YEAR = 2025
SIMULATION_YEARS = 775      # Horizon up to year 2800

# Standard emission schedule periods
STANDARD_PERIODS: list[dict] = [
    {"blocks": 210_000,   "reward": 50},
    {"blocks": 210_000,   "reward": 25},
    {"blocks": 210_000,   "reward": 12.5},
    {"blocks": 210_000,   "reward": 6.25},
    {"blocks": 1_260_000, "reward": 4},
    {"blocks": 2_100_000, "reward": 2},
    {"blocks": 2_100_000, "reward": 1},
]

# Extended emission schedule (Scenario III: Economic circuit breaker)
EXTENDED_PERIODS: list[dict] = STANDARD_PERIODS + [
    {"blocks": 2_100_000, "reward": 1},
]

SCENARIOS: dict[str, dict] = {
    "Scenario_I": {
        "title": "Scenario I (1.3% Loss, 0.5 RIN/Block Final)",
        "loss_rate": 0.013,
        "final_reward": 0.5,
        "periods": STANDARD_PERIODS,
        "milestone_label": "Customized Final Halving => Fixed Reward 0.5 RIN/Block",
    },
    "Scenario_II": {
        "title": "Scenario II: Baseline Protocol (1.5% Loss, 0.6 RIN/Block Final)",
        "loss_rate": 0.015,
        "final_reward": 0.6,
        "periods": STANDARD_PERIODS,
        "milestone_label": "Customized Final Halving => Fixed Reward 0.6 RIN/Block",
    },
    "Scenario_III": {
        "title": "Scenario III: Circuit Breaker (1.5% Loss, Extended 1 RIN Phase)",
        "loss_rate": 0.015,
        "final_reward": 0.6,
        "periods": EXTENDED_PERIODS,
        "milestone_label": "Extended 1 RIN Phase End => Fixed Reward 0.6 RIN/Block",
    },
}


# ==========================================
# 2. Simulation Engine
# ==========================================

def compute_supply_trajectories(
    loss_rate: float,
    final_reward: float,
    periods: list[dict],
    max_supply: float,
    simulation_years: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    """
    Compute the deterministic supply trajectory based on continuous attrition.

    Returns
    -------
    t_array : ndarray — Relative time axis (years from genesis)
    S_arr   : ndarray — Total mined supply S(t)
    C_arr   : ndarray — Real circulating supply C(t) after entropic decay
    t_fix   : float   — Year when scheduled emission ends
    t_trans : float   — Year when macro-hard cap is reached (mining ends)
    """
    D = 1.0 - loss_rate
    gamma = -math.log(D)
    r_fix = BLOCKS_PER_YEAR * final_reward
    stabilizer_fix = r_fix / gamma

    total_blocks_to_fix = sum(p["blocks"] for p in periods)
    t_fix = total_blocks_to_fix / BLOCKS_PER_YEAR
    S_fix = sum(p["blocks"] * p["reward"] for p in periods)
    t_trans = t_fix + (max_supply - S_fix) / r_fix

    # Circulating supply at t_fix via midpoint-decay approximation
    C_fix_computed = 0.0
    cumul_year = 0.0
    for p in periods:
        t_period = p["blocks"] / BLOCKS_PER_YEAR
        mid = cumul_year + t_period / 2
        C_fix_computed += p["blocks"] * p["reward"] * math.exp(-gamma * (t_fix - mid))
        cumul_year += t_period

    C_peak = (
        C_fix_computed * math.exp(-gamma * (t_trans - t_fix))
        + stabilizer_fix * (1 - math.exp(-gamma * (t_trans - t_fix)))
    )

    t_array = np.linspace(0, simulation_years, simulation_years)
    S_arr = np.zeros_like(t_array)
    C_arr = np.zeros_like(t_array)

    for i, t_val in enumerate(t_array):
        if t_val == 0:
            continue

        # --- Total Supply S(t) ---
        if t_val < t_fix:
            cumul_blocks = 0
            sum_supply = 0.0
            for p in periods:
                b, r = p["blocks"], p["reward"]
                if cumul_blocks + b <= BLOCKS_PER_YEAR * t_val:
                    sum_supply += b * r
                    cumul_blocks += b
                else:
                    sum_supply += (BLOCKS_PER_YEAR * t_val - cumul_blocks) * r
                    break
            S_arr[i] = sum_supply
        elif t_fix <= t_val < t_trans:
            S_arr[i] = S_fix + (t_val - t_fix) * r_fix
        else:
            S_arr[i] = max_supply

        # --- Real Circulating Supply C(t) ---
        if t_val < t_fix:
            c_year = 0.0
            sum_c = 0.0
            p_idx = 0
            while (
                p_idx < len(periods)
                and c_year + (periods[p_idx]["blocks"] / BLOCKS_PER_YEAR) <= t_val
            ):
                p = periods[p_idx]
                t_p = p["blocks"] / BLOCKS_PER_YEAR
                mid = c_year + t_p / 2
                sum_c += p["blocks"] * p["reward"] * math.exp(-gamma * (t_val - mid))
                c_year += t_p
                p_idx += 1
            rem_years = t_val - c_year
            if rem_years > 0:
                r_k = BLOCKS_PER_YEAR * periods[p_idx]["reward"]
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
    _OUTPUT_DIR.mkdir(exist_ok=True)

    for scenario_id, config in SCENARIOS.items():
        print(f"Processing {scenario_id}...")

        t_array, S_arr, C_arr, t_fix, t_trans = compute_supply_trajectories(
            config["loss_rate"],
            config["final_reward"],
            config["periods"],
            MAX_SUPPLY,
            SIMULATION_YEARS,
        )

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

        # Plot trajectories
        ax.plot(
            t_array, S_arr,
            label=f"Total Supply $S_{{{scenario_id.split('_')[1]}}}(t)$",
            color="#1565c0", lw=2,
        )
        ax.plot(
            t_array, C_arr,
            label=(
                f"Real Circulating Supply ({config['loss_rate']*100:.1f}% loss per annum)"
                f" $C(t)$"
            ),
            color="#ef6c00", lw=2,
        )

        # Architectural milestones
        ax.axvline(
            x=t_fix, color="gray", linestyle="--", alpha=0.8,
            label=f"{config['milestone_label']} (t = {t_fix:.2f})",
        )
        ax.axvline(
            x=t_trans, color="#c62828", linestyle="--", alpha=0.8,
            label=f"Mining End (t = {t_trans:.2f})",
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
        ax.set_title(
            f"Rincoin Macroeconomic Supply Trajectory (2025-2800)\n{config['title']}",
            fontsize=14, pad=15, fontweight="bold",
        )
        ax.legend(loc="best", framealpha=0.9, fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.7)
        plt.tight_layout()

        output_filename = _OUTPUT_DIR / f"fig_customized_halving_{scenario_id.lower()}.png"
        plt.savefig(output_filename, dpi=300, bbox_inches="tight")
        plt.close()

    print(
        "All customized halving scenarios successfully generated"
        " and saved to output/ directory."
    )


if __name__ == "__main__":
    main()
