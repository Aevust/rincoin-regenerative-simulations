#!/usr/bin/env python3
"""
Rincoin Dual-Layer Temporal Architecture Diagram
=================================================

Generates a high-fidelity architectural schematic illustrating the entropic
flow between the Transactional Layer (Space) and the Rinne Layer (Time).

Usage
-----
    python src/diagrams/dual_layer_architecture.py
"""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OUTPUT_DIR = _REPO_ROOT / "output"


def create_rinnechain_architecture() -> None:
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Visual Styles
    box_style = dict(boxstyle="round,pad=0.3", ec="black", lw=1.5, fc="white")
    layer_bg_style = dict(
        boxstyle="round,pad=0.5", ec="gray", lw=1, fc="#f9f9f9", linestyle="--",
    )

    font_title = {"family": "serif", "weight": "bold", "size": 18}
    font_label = {"family": "serif", "size": 15.5}
    font_small = {"family": "serif", "size": 13.5, "style": "italic"}

    # Layer 1: Transactional Layer (Space) — Top
    rect_trans = patches.FancyBboxPatch((1, 5), 10, 2.5, **layer_bg_style)
    ax.add_patch(rect_trans)
    ax.text(1.2, 7.3, "LAYER 1: Transactional Layer (Space)", **font_title)
    ax.text(
        1.2, 6.8,
        "Function: Value Transfer, Smart Contracts, Active Economy",
        **font_small,
    )

    # Layer 2: Rinne Layer (Time) — Bottom
    rect_rinne = patches.FancyBboxPatch((1, 0.5), 10, 2.5, **layer_bg_style)
    ax.add_patch(rect_rinne)
    ax.text(1.2, 2.75, "LAYER 2: Rinne Layer (Time / Temporal)", **font_title)
    ax.text(
        1.2, 1.9,
        "Function: Proof-of-Temporal-History (PoTH), Entropy Management",
        **font_small,
    )

    # Core Entities
    ax.text(
        3, 6, "Active Addresses\n(High Velocity)",
        ha="center", va="center", bbox=box_style, **font_label,
    )
    ax.text(
        9.0, 6, "Block Generation\n(Consensus)",
        ha="center", va="center", bbox=box_style, **font_label,
    )
    ax.text(
        3, 1.35, "Rinne Addresses\n(Dormant > 400y)",
        ha="center", va="center", bbox=box_style, **font_label,
    )
    ax.text(
        9.5, 1.35, "Reincarnation Event\n(Combustion & Regrowth)",
        ha="center", va="center", bbox=box_style, **font_label,
    )

    # Thermodynamic Flows
    ax.annotate(
        "", xy=(3, 3.0), xytext=(3, 5.3),
        arrowprops=dict(arrowstyle="-", lw=2, color="black"),
    )
    ax.annotate(
        "", xy=(3, 2.1), xytext=(3, 2.7),
        arrowprops=dict(arrowstyle="->", lw=2, color="black"),
    )
    ax.text(
        3.1, 3.8,
        "Thermodynamic Statute of Limitations\n"
        r"(t > $\tau$ $\approx$ 400 years)",
        ha="left", va="center", **font_small,
    )

    ax.annotate(
        "", xy=(7.5, 1.15), xytext=(4.5, 1.15),
        arrowprops=dict(arrowstyle="->", lw=1.5, ls="--"),
    )
    ax.text(5.9, 1.25, "Proof of Rinne (PoR)\nValidation", ha="center", **font_small)

    ax.annotate(
        "", xy=(9, 5.3), xytext=(9, 2.2),
        arrowprops=dict(arrowstyle="->", lw=2, color="black"),
    )
    ax.text(
        9.1, 3.8,
        "Reincarnation (Recycled Supply)\nAdded to Block Reward",
        ha="left", va="center", **font_small,
    )

    ax.annotate(
        "", xy=(4.5, 5.9), xytext=(7.3, 5.9),
        arrowprops=dict(arrowstyle="->", lw=1.5),
    )
    ax.text(5.8, 6.0, "New Issuance", ha="center", **font_small)

    plt.title(
        "Figure: The Rincoin Dual-Layer Temporal Architecture",
        y=0.02, **font_title,
    )

    plt.tight_layout()

    _OUTPUT_DIR.mkdir(exist_ok=True)
    plt.savefig(
        _OUTPUT_DIR / "fig_dual_layer_architecture.png",
        dpi=300, bbox_inches="tight",
    )
    plt.show()


def main() -> None:
    create_rinnechain_architecture()


if __name__ == "__main__":
    main()
