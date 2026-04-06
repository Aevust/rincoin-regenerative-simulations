#!/usr/bin/env python3
"""
Rincoin Regenerative Supply Dynamics (Fully Parameterized Rinne Model)
======================================================================

Simulates the macroeconomic homeostasis achieved by the Proof of Rinne (PoR)
mechanism. Demonstrates the phase transition of value into the Rinnechain
Reserve (R_in) and the perpetual stabilization of the effective circulating
supply (C_Rin).

This script is fully automated. By configuring the ``SCENARIOS`` dictionary,
it handles numerical integration of the Net Liquidity Flux, dynamically
adjusts the time horizon mapping, and outputs high-fidelity plots.

Paper Figures
-------------
- Rinne Scenario I: output/fig_rinne_scenario_i.png

Usage
-----
    python src/deterministic/rinne_supply_dynamics.py
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

BLOCKS_PER_YEAR = 525_600
MAX_SUPPLY = 168_000_000
START_YEAR = 2025
SIMULATION_YEARS = 775       # Horizon up to year 2800
RESOLUTION_MULTIPLIER = 10   # 10x resolution for numerical integration
TAU_DELAY = 200              # Thermodynamic Statute of Limitations (years)

# Extended emission schedule (Scenario III base: Economic circuit breaker)
EXTENDED_PERIODS: list[dict] = [
    {"blocks": 210_000,   "reward": 50},
    {"blocks": 210_000,   "reward": 25},
    {"blocks": 210_000,   "reward": 12.5},
    {"blocks": 210_000,   "reward": 6.25},
    {"blocks": 1_260_000, "reward": 4},
    {"blocks": 2_100_000, "reward": 2},
    {"blocks": 2_100_000, "reward": 1},
    {"blocks": 2_100_000, "reward": 1},   # Extended 1 RIN/block phase
]

SCENARIOS: dict[str, dict] = {
    "Rinne_Scenario_I": {
        "title": "Temporal Evolution of Supply Dynamics and Thermodynamic Equilibrium",
        "subtitle": "Rinne Scenario I (1.5% Loss, 0.6 RIN Final, Extended Phase)",
        "loss_rate": 0.015,
        "final_reward": 0.6,
        "periods": EXTENDED_PERIODS,
        "supply_label": "III",
        "milestone_label": "Extended 1 RIN Phase End => Fixed Reward 0.6 RIN/Block",
    },
}


# ==========================================
# 2. Simulation Engine
# ==========================================

def compute_regenerative_trajectories(
    loss_rate: float,
    final_reward: float,
    periods: list[dict],
    max_supply: float,
    sim_years: int,
    tau_delay: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
    """
    Compute the deterministic supply trajectory including PoR regeneration.

    Returns
    -------
    t_array   : ndarray — High-resolution time axis
    S_arr     : ndarray — Total mined supply S(t)
    C_arr     : ndarray — Baseline circulating supply C(t) (no PoR)
    C_rin_arr : ndarray — Rinne circulating supply C_Rin(t) (with PoR)
    R_in_arr  : ndarray — Rinnechain Reserve R_in(t)
    t_fix     : float   — Year when scheduled emission ends
    t_trans   : float   — Year when macro-hard cap is reached
    """
    D = 1.0 - loss_rate
    gamma = -math.log(D)
    r_fix = BLOCKS_PER_YEAR * final_reward
    stabilizer_fix = r_fix / gamma
    r_post = 0.0
    stabilizer_post = r_post / gamma  # noqa: F841 — kept for clarity

    total_blocks_to_fix = sum(p["blocks"] for p in periods)
    t_fix = total_blocks_to_fix / BLOCKS_PER_YEAR
    S_fix = sum(p["blocks"] * p["reward"] for p in periods)
    t_trans = t_fix + (max_supply - S_fix) / r_fix

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

    # High-resolution time array
    num_points = sim_years * RESOLUTION_MULTIPLIER
    t_array = np.linspace(0, sim_years, num_points)
    dt = t_array[1] - t_array[0]

    S_arr = np.zeros_like(t_array)
    C_arr = np.zeros_like(t_array)

    # --- Baseline Trajectories (Without PoR) ---
    for i, t_val in enumerate(t_array):
        if t_val == 0:
            continue

        # Total Supply S(t)
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

        # Real Circulating Supply C(t)
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

    # --- Regenerative Trajectories (With PoR) ---
    tau_steps = int(tau_delay / dt)
    L_t = S_arr - C_arr
    C_rin_arr = np.copy(C_arr)
    R_in_arr = np.zeros_like(t_array)

    idx_trans = int(np.searchsorted(t_array, t_trans, side="left"))

    # Stabilize C_Rin(t) via perpetual PoR block rewards after mining ends
    for i in range(idx_trans, len(t_array)):
        time_elapsed = t_array[i] - t_trans
        exp_neg = math.exp(-gamma * time_elapsed)
        C_rin_arr[i] = C_peak * exp_neg + stabilizer_fix * (1 - exp_neg)

    # Accumulate R_in(t) via numerical integration of net liquidity flux
    cum_delta = 0.0
    for i in range(len(t_array)):
        past_i = i - tau_steps
        if t_array[i] < tau_delay or past_i < 0:
            R_in_arr[i] = 0
        elif t_array[i] < t_trans:
            R_in_arr[i] = L_t[past_i]
        else:
            c_past = C_rin_arr[past_i] if past_i >= 0 else 0
            delta = gamma * c_past - r_fix
            cum_delta += delta * dt
            R_in_arr[i] = R_in_arr[idx_trans - 1] + cum_delta

    return t_array, S_arr, C_arr, C_rin_arr, R_in_arr, t_fix, t_trans


# ==========================================
# 3. Execution & Automated Plotting
# ==========================================

def main() -> None:
    _OUTPUT_DIR.mkdir(exist_ok=True)

    for scenario_id, config in SCENARIOS.items():
        print(f"Processing {scenario_id}...")

        t_array, S_arr, C_arr, C_rin_arr, R_in_arr, t_fix, t_trans = (
            compute_regenerative_trajectories(
                config["loss_rate"],
                config["final_reward"],
                config["periods"],
                MAX_SUPPLY,
                SIMULATION_YEARS,
                TAU_DELAY,
            )
        )

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

        lbl_s = config["supply_label"]
        loss_pct = config["loss_rate"] * 100

        # Plot all four state curves
        ax.plot(
            t_array, S_arr,
            label=f"Total Supply $S_{{{lbl_s}}}(t)$",
            color="#1565c0", lw=2,
        )
        ax.plot(
            t_array, C_arr,
            label=f"Normal Real Circulating Supply ({loss_pct:.1f}% loss per year) $C_{{{lbl_s}}}(t)$",
            color="#ef6c00", lw=2,
        )
        ax.plot(
            t_array, C_rin_arr,
            label=r"Rinne Circulating Supply with Reincarnation $C_{Rin}(t)$",
            color="#00b0ff", lw=2,
        )
        ax.plot(
            t_array, R_in_arr,
            label=r"$R_{in}(t)$ (Rinnechain Supply)",
            color="#d32f2f", lw=2,
        )

        # Architectural milestones
        ax.axvline(
            x=t_fix, color="gray", linestyle="--", alpha=0.8,
            label=f"{config['milestone_label']} (t = {t_fix:.2f})",
        )
        ax.axvline(
            x=t_trans, color="#c62828", linestyle="--", alpha=0.8,
            label=f"Mining End & Reincarnation Cycle Start (t = {t_trans:.2f})",
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
            f"{config['title']}\n{config['subtitle']}",
            fontsize=14, pad=15, fontweight="bold",
        )
        ax.legend(loc="best", framealpha=0.9, fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.7)
        plt.tight_layout()

        output_filename = _OUTPUT_DIR / f"fig_{scenario_id.lower()}.png"
        plt.savefig(output_filename, dpi=300, bbox_inches="tight")
        plt.close()

    print("Rinne Scenario successfully generated and saved to output/ directory.")


if __name__ == "__main__":
    main()
