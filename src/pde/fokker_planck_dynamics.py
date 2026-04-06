#!/usr/bin/env python3
"""
Rincoin Fokker-Planck (Kolmogorov Forward) Equation Visualization
=================================================================

Illustrates the phase transition of the wealth distribution u(t,x):

1. **Standard PoW (Heat Death)**: Infinite accumulation of dormant capital
   creates a heavy-tailed distribution (Dead Whales).
2. **Rincoin PoR (Non-Equilibrium Steady State)**: The Thermodynamic Statute
   of Limitations cleanly truncates the dead tail, recirculating the mass
   via the PoR engine to active participants, maintaining homeostasis.

This script is fully automated: adjustments to the cut-off threshold or
distribution parameters will dynamically recalculate mass conservation,
injection profiles, and plotting annotations.

Usage
-----
    python src/pde/fokker_planck_dynamics.py
"""

import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm, gamma

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OUTPUT_DIR = _REPO_ROOT / "output"


# ==========================================
# 1. System Parameters & Distribution Setup
# ==========================================

X_MIN = 0.1
X_MAX = 150
NUM_POINTS = 1000

# Base Wealth Distribution Parameters (Lognormal approximation for PoW)
LOGNORM_S = 1.2
LOGNORM_SCALE = 15

# Rincoin Thermodynamic Parameters
CUTOFF_THRESHOLD = 80       # Thermodynamic Statute of Limitations (tau)
INJECTION_A = 2.5           # Shape parameter for recirculation (Gamma dist)
INJECTION_SCALE = 4.0       # Scale parameter for recirculation (Gamma dist)


# ==========================================
# 2. Main Execution
# ==========================================

def main() -> None:
    x_array = np.linspace(X_MIN, X_MAX, NUM_POINTS)
    dx = x_array[1] - x_array[0]

    # Standard PoW State (Heat Death)
    u_pow = lognorm.pdf(x_array, s=LOGNORM_S, scale=LOGNORM_SCALE)

    # Rincoin PoR State (Non-Equilibrium Steady State)
    u_rin = np.copy(u_pow)
    tail_mask = x_array >= CUTOFF_THRESHOLD
    tail_mass = np.sum(u_rin[tail_mask]) * dx

    u_rin[tail_mask] = 0.0

    injection_profile = gamma.pdf(x_array, a=INJECTION_A, scale=INJECTION_SCALE)
    injection_profile /= np.sum(injection_profile) * dx

    u_rin += injection_profile * tail_mass

    injection_peak_x = x_array[np.argmax(injection_profile)]
    injection_peak_y = np.max(injection_profile * tail_mass)

    # ---- Dual-Panel Plot ----
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Upper Panel: Standard PoW
    axes[0].plot(
        x_array, u_pow, color="gray", linewidth=2,
        label=r"Standard PoW Distribution $u(t,x)$",
    )
    axes[0].fill_between(
        x_array, u_pow, where=tail_mask,
        color="black", alpha=0.4, label="Dead Whales (Trapped Entropy)",
    )
    axes[0].fill_between(x_array, u_pow, where=~tail_mask, color="lightgray", alpha=0.5)

    axes[0].set_title(
        "Standard PoW Blockchain (Heat Death): Infinite Accumulation of Dead Capital",
        fontsize=14, fontweight="bold",
    )
    axes[0].set_ylabel(r"Density of Wallets $u(t,x)$", fontsize=12)
    axes[0].legend(fontsize=11, loc="upper right")
    axes[0].grid(True, linestyle=":", alpha=0.7)

    # Lower Panel: Rincoin PoR Engine
    axes[1].plot(
        x_array, u_rin, color="darkorange", linewidth=2,
        label=r"Rincoin Steady State Distribution $u^{ss}(x)$",
    )
    axes[1].fill_between(x_array, u_rin, color="orange", alpha=0.3)
    axes[1].axvline(
        x=CUTOFF_THRESHOLD, color="red", linestyle="--", linewidth=2,
        label="Thermodynamic Statute of Limitations (Cut-off)",
    )

    axes[1].annotate(
        "Combustion & Reincarnation\n(Tail mass recycled to active economy)",
        xy=(injection_peak_x, injection_peak_y + 0.005),
        xytext=(CUTOFF_THRESHOLD + 5, np.max(u_rin) * 0.4),
        arrowprops=dict(facecolor="red", shrink=0.05, width=2, headwidth=8),
        fontsize=11, color="red", fontweight="bold",
        ha="left", va="center",
    )

    axes[1].set_title(
        "Rincoin Regenerative Engine: Phase Transition to a Non-Equilibrium Steady State",
        fontsize=14, fontweight="bold",
    )
    axes[1].set_xlabel(r"Wallet Balance $x$ (RIN)", fontsize=12)
    axes[1].set_ylabel(r"Density of Wallets $u(t,x)$", fontsize=12)
    axes[1].legend(fontsize=11, loc="upper right")
    axes[1].grid(True, linestyle=":", alpha=0.7)

    plt.tight_layout()

    _OUTPUT_DIR.mkdir(exist_ok=True)
    plt.savefig(
        _OUTPUT_DIR / "fig_fokker_planck.png",
        dpi=300, bbox_inches="tight",
    )
    plt.show()


if __name__ == "__main__":
    main()
