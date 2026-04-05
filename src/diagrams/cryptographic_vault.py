#!/usr/bin/env python3
"""
Rincoin Cryptographic Vault & Epoch Sweeper Dynamics Diagram
============================================================

Generates a high-fidelity architectural schematic illustrating the bifurcation
of entropic flow at the Cryptographic Event Horizon (tau_c).

Visualizes the structural separation between the Active Economy, the
Vulnerable Latent Phase, and the perfectly shielded Cryptographic Vault.

Usage
-----
    python src/diagrams/cryptographic_vault.py
"""

import os

import matplotlib.pyplot as plt
import matplotlib.patches as patches


def create_cryptographic_vault_dynamics_diagram() -> None:
    fig, ax = plt.subplots(figsize=(16, 10), dpi=200)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Visual Styles
    box_style = dict(boxstyle="round,pad=0.4", ec="black", lw=1.5, fc="white")
    vault_box_style = dict(boxstyle="round,pad=0.4", ec="#6a1b9a", lw=2, fc="#f3e5f5")
    layer_bg_style = dict(
        boxstyle="round,pad=0.5", ec="gray", lw=1, fc="#f9f9f9", linestyle="--",
    )

    font_title = {"family": "serif", "weight": "bold", "fontsize": 20}
    font_sub_title = {"family": "serif", "weight": "bold", "fontsize": 17}
    font_label = {"family": "serif", "fontsize": 15}
    font_small = {"family": "serif", "fontsize": 13}
    font_highlight = {
        "family": "serif", "fontsize": 15, "weight": "bold", "color": "#c62828",
    }
    font_vault_tech = {
        "family": "serif", "fontsize": 13, "style": "italic", "color": "#6a1b9a",
    }

    # Layer 1: Transactional Layer (Space)
    rect_trans = patches.FancyBboxPatch((0.5, 4.5), 15, 5.0, **layer_bg_style)
    ax.add_patch(rect_trans)
    ax.text(0.7, 9.1, "LAYER 1: Transactional Layer (Space)", **font_sub_title)

    # Layer 2: Rinne Layer (Time)
    rect_rinne = patches.FancyBboxPatch(
        (0.5, 0.5), 15, 3.5, **layer_bg_style, facecolor="#e1f5fe",
    )
    ax.add_patch(rect_rinne)
    ax.text(0.7, 3.6, "LAYER 2: Rinne Layer (Time / PoR Reserve Pool)", **font_sub_title)

    # Core Entities
    ax.text(
        2.5, 8.5, "Active Economy ($C$)\n(High Velocity)",
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.4", ec="black", lw=1.5, fc="#e8f5e9"),
        **font_label,
    )
    ax.text(
        2.5, 5.5,
        r"Vulnerable Latent Phase ($D$)" + "\n" + r"$t < \tau_c$" + "\n(User Key Control)",
        ha="center", va="center",
        bbox=dict(
            boxstyle="round,pad=0.4", ec="black", lw=1.5,
            fc="#fff9c4", linestyle="dotted",
        ),
        **font_label,
    )

    # Cryptographic Event Horizon
    node_epoch = patches.Circle((8, 5.5), 0.3, ec="#c62828", lw=2, fc="white", zorder=3)
    ax.add_patch(node_epoch)
    ax.text(
        8, 6.6, r"Cryptographic" + "\n" + r"Event Horizon ($t = \tau_c$)",
        ha="center", va="center", **font_highlight,
    )
    ax.text(
        7.6, 5.0, "Trigger:\n[Sweeper Gold Rush]",
        ha="right", va="center", **font_highlight,
    )

    # The Cryptographic Vault
    ax.text(
        8, 4.1, "THE CRYPTOGRAPHIC VAULT (Smart Contract Address)",
        ha="center", **font_title, color="#6a1b9a",
    )
    rect_vault = patches.FancyBboxPatch(
        (4.7, 1.0), 6.5, 3.0, **vault_box_style, zorder=1,
    )
    ax.add_patch(rect_vault)
    ax.text(
        8, 2.4,
        r"SHIELDED LATENT STATE ($V$)"
        + "\nCryptographic Maturation Pipeline\n"
        + r"$t \in (\tau_c, \tau)$",
        ha="center", va="center", bbox=box_style, **font_label, zorder=2,
    )
    ax.text(
        7.0, 1.4,
        "Algorithm:\nNew Address Generation\nper Maturation Block",
        ha="left", va="center", **font_vault_tech,
    )

    # Recirculation Mechanisms
    ax.text(
        13.5, 7.5,
        r"Sweeper Bounty" + "\n" + r"Recirculation ($\beta \approx 2\%$)",
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.4", ec="#1565c0", lw=1.5, fc="#e3f2fd"),
        **font_label,
    )
    ax.text(
        13.5, 6.0,
        r"ZKP Owner Recovery" + "\n" + r"Recirculation ($\gamma \approx 10\%$)",
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.4", ec="#1565c0", lw=1.5, fc="#e3f2fd"),
        **font_label,
    )

    # Layer 2 PoR Reserve Pool
    ax.text(
        1.7, 2.4,
        r"Rinne addresses ($t > \tau$)" + "\n" + r"PoR Reserve Pool ($R_{in}$)",
        ha="center", va="center", bbox=box_style, **font_label,
    )

    # Thermodynamic Flows
    arrow_active = dict(arrowstyle="-|>", color="black", lw=1.5, mutation_scale=20)

    ax.annotate("", xy=(2.5, 6.3), xytext=(2.5, 7.9), arrowprops=arrow_active)
    ax.text(2.6, 7.1, "Entropy Loss\n(Inactive UTXO)", **font_small)

    ax.annotate("", xy=(7.5, 5.5), xytext=(4.3, 5.5), arrowprops=arrow_active)
    ax.text(6.0, 5.65, r"$loss \times \tau_c$" + "\nMaturation", ha="center", **font_small)

    ax.annotate(
        "", xy=(8, 4.4), xytext=(8, 5.2),
        arrowprops=dict(arrowstyle="-|>", color="#c62828", lw=2.5, mutation_scale=25),
    )
    ax.text(
        8.5, 5.0,
        r"FORCED EXTRACTION:" + "\n" + r"Total Sweep Mass $D + loss$",
        ha="left", va="center", **font_small, color="#c62828",
    )

    ax.annotate(
        "", xy=(11.6, 7.3), xytext=(8.4, 5.5),
        arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5, mutation_scale=20),
    )
    ax.annotate(
        "", xy=(11.6, 5.9), xytext=(8.4, 5.5),
        arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5, mutation_scale=20),
    )

    ax.annotate(
        "", xy=(4.5, 8.7), xytext=(13.5, 8.1),
        arrowprops=dict(
            arrowstyle="-|>", color="black", lw=1.5,
            mutation_scale=20, connectionstyle="arc3,rad=0.1",
        ),
    )
    ax.annotate(
        "", xy=(4.5, 8.3), xytext=(13.3, 6.6),
        arrowprops=dict(
            arrowstyle="-|>", color="black", lw=1.5,
            mutation_scale=20, connectionstyle="arc3,rad=0.15",
        ),
    )

    ax.annotate(
        "", xy=(8, 3.0), xytext=(8, 4.0),
        arrowprops=dict(arrowstyle="-|>", color="#7b1fa2", lw=2.5, mutation_scale=25),
    )
    ax.text(
        8.2, 3.6,
        r"SHIELDING: Thermodynamic Lock"
        + "\n"
        + r"Mass $= Total \times (1-\beta) \times (1-\gamma)$",
        ha="left", va="center", **font_small, color="#7b1fa2",
    )

    ax.annotate(
        "", xy=(3.3, 2.4), xytext=(5.5, 2.4),
        arrowprops=dict(arrowstyle="-|>", color="#0068b7", lw=2.5, mutation_scale=25),
    )
    ax.text(
        2.8, 1.7,
        r"Algorithmic Expulsion (L1 $\to$ L2)"
        + "\n"
        + r"Deterministic Condition: $CVT \geq \tau_V$",
        ha="left", va="center", **font_small, color="#0068b7",
    )

    plt.title(
        "Figure: The Cryptographic Vault and Epoch Sweeper Dynamics",
        y=0.01, **font_title,
    )

    plt.tight_layout()

    os.makedirs("output", exist_ok=True)
    plt.savefig(
        "output/fig_cryptographic_vault.png",
        dpi=300, bbox_inches="tight",
    )
    plt.show()


def main() -> None:
    create_cryptographic_vault_dynamics_diagram()


if __name__ == "__main__":
    main()
