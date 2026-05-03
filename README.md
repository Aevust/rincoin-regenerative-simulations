# Rincoin Regenerative Simulations

**Rigorous Monte Carlo and deterministic validation of the Regenerative Thermodynamic Security framework**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17141922.svg)](https://doi.org/10.5281/zenodo.17141922)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Vectorized-013243.svg)](https://numpy.org/)

---

## Overview

This repository provides the **complete, reproducible simulation suite** accompanying the paper:

> *On the Convergence of Regenerative Thermodynamic Security and Economic Incentives* (Rincoin v1.6.2)

Legacy Proof-of-Work blockchains suffer from an irreversible thermodynamic pathology: private keys are lost, holders die, and coins become permanently inaccessible. Over centuries, this monotonic increase in entropy drives the circulating supply toward zero — a macroeconomic **heat death** analogous to the Second Law of Thermodynamics. The resulting wealth concentration among "dead whales" is not merely an inconvenience; it is a fundamental violation of the economic sustainability axiom upon which any monetary system must rest.

Rincoin's **Proof-of-Rinne (PoR)** protocol resolves this by introducing a thermodynamically grounded recirculation mechanism:

1. **Entropic Decay** — Coins whose cryptographic keys have not demonstrated liveness beyond a statute-of-limitations threshold (tau) are probabilistically identified as dormant.
2. **Sweeper Gold Rush** — At each cryptographic epoch boundary (tau_c), dormant mass is extracted and a competitive bounty (beta ~ 2%) is recirculated to active participants.
3. **ZKP Owner Recovery** — Legitimate owners may reclaim a fraction (gamma ~ 10%) of their dormant balance via zero-knowledge proof, preserving individual property rights while maintaining systemic homeostasis.
4. **Cryptographic Vault** — The remaining mass is permanently locked into a shielded smart-contract address, algorithmically expelled to the Layer 2 PoR Reserve Pool upon maturation.

The simulations in this repository prove — via **Stochastic Differential Equations (SDE)**, **Fokker-Planck partial differential equations (PDE)**, **deterministic macro-hard-cap trajectory analysis**, and fully vectorized **Monte Carlo methods** with up to N = 100,000 paths — that this mechanism drives the circulating supply to a **non-equilibrium steady state** that constitutes a **Nash Equilibrium**: no rational agent can improve their payoff by unilaterally deviating from the protocol.

---

## Directory Structure

```
rincoin-regenerative-simulations/
├── README.md
├── LICENSE                         # MIT License
├── requirements.txt                # Python dependencies
├── .gitignore
│
├── src/
│   ├── sde/                        # Stochastic Differential Equation models
│   │   ├── sde_baseline.py         # Pure thermodynamic SDE (Euler-Maruyama)
│   │   ├── sde_sweeper_bounty.py   # Epoch sweeper with bounty recirculation
│   │   ├── sde_4panel_recovery.py  # 4-panel micro/macro ZKP recovery comparison
│   │   └── sde_zkp_recovery_overlay.py  # Nash equilibrium proof (high-resolution)
│   │
│   ├── pde/                        # Partial Differential Equation models
│   │   └── fokker_planck_dynamics.py  # Wealth distribution phase transition
│   │
│   ├── deterministic/              # Deterministic macroeconomic supply models
│   │   ├── baseline_supply_dynamics.py      # Standard halving baseline trajectory
│   │   ├── customized_halving_scenarios.py  # Halving + entropic decay trajectories
│   │   └── rinne_supply_dynamics.py         # PoR regeneration & R_in accumulation
│   │
│   ├── diagrams/                   # Architectural & concept diagrams
│   │   ├── dual_layer_architecture.py  # L1 (Space) / L2 (Time) schematic
│   │   └── cryptographic_vault.py      # Vault bifurcation dynamics
│   │
│   └── spde/                       # [Future] Stochastic PDE extensions
│       └── .gitkeep
│
├── output/                         # Generated figures (git-ignored PNGs)
├── notebooks/                      # Jupyter notebook versions (optional)
└── docs/                           # Supplementary documentation
```

---

## Installation

### Prerequisites

- Python 3.10 or later
- pip (or any PEP 517-compatible installer)

### Setup

```bash
git clone https://github.com/Aevust/rincoin-regenerative-simulations.git
cd rincoin-regenerative-simulations

python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### Verify

```bash
python src/sde/sde_baseline.py
```

A matplotlib window should open, displaying the baseline stochastic supply simulation.

---

## Reproducing the Paper's Figures

Every script is **fully parameterized**: edit the constants at the top of the file, and all titles, reference lines, statistical bounds, and annotations will auto-update.

### SDE Models

| Paper Figure | Script | Key Parameters to Set |
|:---|:---|:---|
| **Figure 7 (Upper)** — Baseline (21M, mu=1.5%) | `src/sde/sde_baseline.py` | `INITIAL_SUPPLY=21_000_000`, `BASE_LOSS_RATE=0.015`, `NUM_SIMULATIONS=1000` |
| **Figure 7 (Lower)** — Baseline (21M, mu=1.6%) | `src/sde/sde_baseline.py` | `INITIAL_SUPPLY=21_000_000`, `BASE_LOSS_RATE=0.016`, `NUM_SIMULATIONS=1000` |
| **Figure 8 (Upper)** — Oversupply (28M, mu=1.5%) | `src/sde/sde_baseline.py` | `INITIAL_SUPPLY=28_000_000`, `BASE_LOSS_RATE=0.015`, `NUM_SIMULATIONS=1000` |
| **Figure 8 (Lower)** — Oversupply (28M, mu=1.6%) | `src/sde/sde_baseline.py` | `INITIAL_SUPPLY=28_000_000`, `BASE_LOSS_RATE=0.016`, `NUM_SIMULATIONS=1000` |
| **Figure 9** — Sweeper Bounty Only (21M) | `src/sde/sde_sweeper_bounty.py` | `INITIAL_SUPPLY=21_000_000`, `MU_1=0.015`, `MU_2=0.016`, `NUM_SIMULATIONS=1000` |
| **Figure 10** — Sweeper Bounty Only (28M) | `src/sde/sde_sweeper_bounty.py` | `INITIAL_SUPPLY=28_000_000`, `MU_1=0.015`, `MU_2=0.016`, `NUM_SIMULATIONS=1000` |
| **Figure 12 (Upper)** — 4-Panel Recovery (21M, mu=1.5%) | `src/sde/sde_4panel_recovery.py` | `INITIAL_SUPPLY=21_000_000`, `MU=0.015`, `NUM_SIMS=1000` |
| **Figure 12 (Lower)** — Overlay (21M, mu=1.5%) | `src/sde/sde_zkp_recovery_overlay.py` | `INITIAL_SUPPLY=21_000_000`, `MU=0.015`, `NUM_SIMS=20_000` |
| **Figure 13 (Upper)** — 4-Panel Recovery (21M, mu=1.6%) | `src/sde/sde_4panel_recovery.py` | `INITIAL_SUPPLY=21_000_000`, `MU=0.016`, `NUM_SIMS=1000` |
| **Figure 13 (Lower)** — Overlay (21M, mu=1.6%) | `src/sde/sde_zkp_recovery_overlay.py` | `INITIAL_SUPPLY=21_000_000`, `MU=0.016`, `NUM_SIMS=20_000` |
| **Figure 14 (Upper)** — 4-Panel Recovery (21M, mu=1.7%) | `src/sde/sde_4panel_recovery.py` | `INITIAL_SUPPLY=21_000_000`, `MU=0.017`, `NUM_SIMS=1000` |
| **Figure 14 (Lower)** — "The Miracle of Equilibrium" | `src/sde/sde_zkp_recovery_overlay.py` | `INITIAL_SUPPLY=21_000_000`, `MU=0.017`, `NUM_SIMS=100_000` |
| **Figure 15 (Upper)** — 4-Panel Recovery (28M, mu=1.5%) | `src/sde/sde_4panel_recovery.py` | `INITIAL_SUPPLY=28_000_000`, `MU=0.015`, `NUM_SIMS=1000` |
| **Figure 15 (Lower)** — Overlay (28M, mu=1.5%) | `src/sde/sde_zkp_recovery_overlay.py` | `INITIAL_SUPPLY=28_000_000`, `MU=0.015`, `NUM_SIMS=20_000` |
| **Figure 16 (Upper)** — 4-Panel Recovery (28M, mu=1.6%) | `src/sde/sde_4panel_recovery.py` | `INITIAL_SUPPLY=28_000_000`, `MU=0.016`, `NUM_SIMS=1000` |
| **Figure 16 (Lower)** — Overlay (28M, mu=1.6%) | `src/sde/sde_zkp_recovery_overlay.py` | `INITIAL_SUPPLY=28_000_000`, `MU=0.016`, `NUM_SIMS=20_000` |
| **Figure 17 (Upper)** — 4-Panel Recovery (28M, mu=1.7%) | `src/sde/sde_4panel_recovery.py` | `INITIAL_SUPPLY=28_000_000`, `MU=0.017`, `NUM_SIMS=1000` |
| **Figure 17 (Lower)** — Absolute Nash Equilibrium | `src/sde/sde_zkp_recovery_overlay.py` | `INITIAL_SUPPLY=28_000_000`, `MU=0.017`, `NUM_SIMS=100_000` |

### Deterministic Supply Trajectories

| Paper Figure | Script | Description |
|:---|:---|:---|
| **Figure 1** — Baseline Standard | `src/deterministic/baseline_supply_dynamics.py` | Nakamoto-style halving schedule baseline trajectory |
| **Figure 2, 3, 4** — Customized Halvings | `src/deterministic/customized_halving_scenarios.py` | Macro-hard cap vs. Real circulating supply mapping |
| **Figure 6** — Rinne Scenario I | `src/deterministic/rinne_supply_dynamics.py` | PoR dynamic phase transition & steady state |

The Baseline script outputs the standard halving reference; the three Customized Halving scenarios are generated in a single run, each saving its own PNG. The Rinne script outputs the full four-curve overlay (S, C, C_Rin, R_in).

### PDE & Concept Diagrams

| Paper Figure | Script | Description |
|:---|:---|:---|
| **Figure 5** — Dual-Layer Architecture | `src/diagrams/dual_layer_architecture.py` | L1 Transactional (Space) / L2 Rinne (Time) schematic |
| **Figure 11** — Cryptographic Vault | `src/diagrams/cryptographic_vault.py` | Vault bifurcation and epoch sweeper dynamics |
| **Figure 18** — Fokker-Planck Dynamics | `src/pde/fokker_planck_dynamics.py` | PoW heat death vs. PoR steady-state wealth distribution |

### Quick Reproduction (All Core Figures)

```bash
# Baseline scenarios
python src/sde/sde_baseline.py

# Sweeper bounty mechanism
python src/sde/sde_sweeper_bounty.py

# 4-panel micro/macro comparison
python src/sde/sde_4panel_recovery.py

# Nash equilibrium overlay (high resolution — see Performance Note below)
python src/sde/sde_zkp_recovery_overlay.py

# Deterministic baseline (standard Nakamoto halving)
python src/deterministic/baseline_supply_dynamics.py

# Deterministic macro-hard-cap trajectories (3 customized scenarios)
python src/deterministic/customized_halving_scenarios.py

# Proof of Rinne regenerative dynamics
python src/deterministic/rinne_supply_dynamics.py

# Fokker-Planck wealth distribution
python src/pde/fokker_planck_dynamics.py

# Architectural diagrams
python src/diagrams/dual_layer_architecture.py
python src/diagrams/cryptographic_vault.py
```

---

## Performance Note

The **ZKP Recovery Overlay** model (`sde_zkp_recovery_overlay.py`) at its most demanding configuration — `MU=0.017`, `NUM_SIMS=100,000` — processes state matrices of shape `(100_000, 401)`. Each individual matrix requires approximately 320 MB of contiguous memory; however, the vectorized simulation engine simultaneously allocates five such arrays (C, D, V, Z\_loss, Z\_rec) per run, and `main()` executes two runs (Scenario A and B). The resulting **peak memory footprint is approximately 1.6 GB**. A preflight check built into the script will print a warning if the estimated allocation exceeds 2 GB.

All simulation engines in this repository are **fully vectorized** using NumPy's strided memory model:

- **No Python-level loops over simulation paths.** The inner loop iterates over time steps only (401 iterations for a 400-year horizon). Within each step, all N paths are updated simultaneously via vectorized array operations.
- **Boolean masking** for discrete epoch events: `sweep_mask = next_sweep_timer <= 0` produces a binary selector over all N paths in O(N) time, eliminating branching overhead.
- **Pre-allocated random variates**: The entire Wiener process `Z ~ N(0,1)` of shape `(N, T)` is generated in a single call to `np.random.normal`, enabling cache-friendly sequential access during the time-stepping loop.

| Configuration | N | Approx. Wall Time | Memory |
|:---|---:|---:|---:|
| Baseline SDE | 1,000 | < 1 s | ~3 MB |
| Sweeper Bounty | 1,000 | < 2 s | ~6 MB |
| 4-Panel Recovery | 1,000 | < 3 s | ~10 MB |
| ZKP Overlay (mu=0.015) | 20,000 | ~10 s | ~60 MB |
| ZKP Overlay (mu=0.016) | 20,000 | ~10 s | ~60 MB |
| **ZKP Overlay (mu=0.017)** | **100,000** | **~50 s** | **~1.6 GB peak** |
| **ZKP Overlay (mu=0.017~)** | **500,000** | **~100 s** | **~15 GB peak** |
| **ZKP Overlay (mu=0.017~)** | **1,000,000** | **~180 s** | **~30.0 GB peak** |

> **Note**: Peak memory accounts for all 5 pre-allocated arrays (C, D, V, Z\_loss, Z\_rec) across 2 simulation runs. On machines with less than 4 GB of free RAM, reduce `NUM_SIMS` to `20_000`.

*Benchmarks measured on an Apple M2 Pro (12-core) with NumPy 1.26. Intel/AMD systems with AVX-512 may observe faster throughput on the N=100,000 configuration due to wider SIMD lanes.*

---

## Mathematical Foundation

### Governing SDE (Euler-Maruyama Discretization)

The circulating supply `C(t)` evolves according to:

```
dC_t = r_f dt - C_t (mu dt + sigma dW_t)
```

where:
- `r_f` — Deterministic annual issuance (0.6 RIN/block x 525,600 blocks/year)
- `mu` — Mean entropic loss rate (base loss)
- `sigma` — Volatility of the stochastic loss rate
- `dW_t` — Standard Wiener process increment

### Theoretical Steady-State Equilibrium

For the bounty-only model (no ZKP recovery):

```
C* = r_f / [mu * (1 - beta)]
```

With ZKP owner recovery (gamma ~ 10%):

```
C** = r_f / [mu * (1 - beta) * (1 - gamma)]
```

The paper proves that for `mu = 0.017` and `gamma = 0.10`, `C**` converges to the Nakamoto target of 21,000,000 RIN — the Nash Equilibrium.

### Deterministic Macro-Hard-Cap and PoR Phase Transition

The deterministic models track the total mined supply `S(t)` under a customized halving schedule, and the real circulating supply `C(t)` subject to continuous exponential attrition at rate `gamma = -ln(1 - loss_rate)`:

```
C(t) = sum_k [ B_k * r_k * exp(-gamma * (t - t_k_mid)) ]       (during scheduled emission)
C(t) = C_fix * exp(-gamma * (t - t_fix)) + (r_f / gamma) * (1 - exp(-gamma * (t - t_fix)))   (fixed-reward phase)
```

After mining ceases (`t > t_trans`), the Proof of Rinne mechanism sustains `C_Rin(t)` at the stabilizer level `r_f / gamma` by recycling matured dormant coins as block rewards, while the Rinnechain Reserve `R_in(t)` accumulates via the delayed net liquidity flux `L(t - tau)`. This dual-curve separation proves that the protocol achieves a **thermodynamic steady state** without any new coin creation beyond the 168M macro-hard cap.

### Fokker-Planck (Kolmogorov Forward) Equation

The wealth distribution `u(t,x)` evolves under:

```
du/dt = -d/dx [A(x) u] + (1/2) d^2/dx^2 [B(x)^2 u]
```

The PoR mechanism introduces a **truncation operator** at the statute-of-limitations threshold `tau`, eliminating the heavy tail of dead capital and re-injecting mass into the active economy via a Gamma-distributed profile — establishing a non-equilibrium steady state `u^{ss}(x)`.

---

## Future Work

The `src/spde/` directory is reserved for planned extensions:

- **SPDE (Stochastic Partial Differential Equations)**: Spatially-extended models coupling the Fokker-Planck wealth distribution with stochastic forcing terms, enabling analysis of local equilibria and spatial heterogeneity in adoption dynamics.
- **Network Topology Models**: Agent-based simulations on scale-free and small-world graphs, modeling peer-to-peer propagation of epoch sweeps and the formation of sweeper coalitions.
- **Multi-Asset Interactions**: Cross-chain thermodynamic coupling between Rincoin and legacy PoW chains, modeling entropy transfer at bridge interfaces.
- **Empirical Calibration**: Parameter estimation from real-world Bitcoin UTXO dormancy data to calibrate `mu`, `sigma`, and epoch distributions.

Contributions in these directions are welcome. Please open an issue to discuss scope before submitting a pull request.

---

## Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/spde-spatial-model`)
3. Ensure all existing scripts still execute without error
4. Add tests or validation notebooks for new models
5. Submit a pull request with a clear description of the mathematical model and its relation to the paper

---

## Citation

If you use this code in academic work, please cite:

```bibtex
@software{tokino2026rincoin,
  title        = {On the Convergence of Regenerative Thermodynamic Security and Economic Incentives (Rincoin v1.6.2)},
  author       = {Tokino, Michiru},
  year         = {2026},
  version      = {1.6.2},
  publisher    = {Zenodo},
  note         = {Rincoin Whitepaper v1.6.2 — Simulation Suite},
  doi          = {10.5281/zenodo.17141922},
  url          = {https://github.com/Aevust/rincoin-regenerative-simulations}
}
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
