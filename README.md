# INNOVECMO Benchmarks

This repository serves as a collection of benchmarks and problems for the **INNOVECMO** project. The project focuses on the development and validation of an innovative, valveless, wave-driven pumping concept (Liebau-based pump) for Extracorporeal Membrane Oxygenation (ECMO) systems.

## Project Overview

The INNOVECMO project aims to provide a viable alternative to current rotary (centrifugal) ECMO pumps. By leveraging the Liebau principle—where periodic external compression of a compliant tube generates net directional flow—the project seeks to restore physiologically relevant pulsatility while minimizing blood damage (hemolysis and thrombogenesis) associated with high-shear rotary blades.

### Simulation Roadmap
The project follows a hierarchical, multi-stage strategy to ensure numerical robustness and scientific validation:

1.  **Phase I: Structural Truth (Empty Prestressed Tube)**
    - **Status**: [FOM Scripts Ready]
    - Reproduce large-deformation behavior and contact patterns of the empty silicone tube.
    - **Implementation**: Multi-stage Python script (`MainKratos_FOM.py`) handles axial stretching (0-1s) followed by vertical pinching (1-2s).
    - **Symmetric Boundary Conditions**: The model applies a symmetric axial pull of $\pm 1$ mm ($2$ mm total stretch) to maintain the central section at $Z=0$ for improved stability and visualization.
    - **Pre-stress Rationale**: An axial pre-strain of **$2\%$** is applied to emulate real-world clinical assembly. This ensures the compliant tube remains taut, preventing structural buckling during high-frequency actuation and shifting the system's resonant response to the target clinical range.
    - **Validation**: Compare against experimental segmented contours.

![Final Displacement Animation](file:///home/kratos/INNOVECMO_Benchmarks/Benchmarks/Stage1_Structural/tube_displacement.gif)
*Animation of the two-stage structural response. Stage 1 (0-1s): Symmetric Axial stretching. Stage 2 (1-2s): Vertical pinching. Colormap represents displacement magnitude with dynamic scaling for maximum detail.*

![Boundary Regions](file:///home/kratos/INNOVECMO_Benchmarks/Figures/Pinching_and_End_Boundaries.png)
*Definition of End Boundaries and Pinching Zones (Top/Bottom).*
2.  **Phase II: Projection-based Structural ROM**
    - Construct a reduced-order model (ROM) to compress the structural response manifold.
    - Accelerates the generation of training data for subsequent stages.
3.  **Phase III: Manifold Reduced Model (M-ROM)**
    - Capture the nonlinear solution manifold for efficient design exploration and real-time control.
4.  **Phase IV: Coupling with 1D Hemodynamic Fluid Model**
    - Use a 1D wave-propagation model (Kratos) to solve for pressure and flow.
    - **Coupling variable**: Local cross-sectional area evolution.
    - **Objective**: Capture system-level wave dynamics and interference while maintaining geometric richness in the actuation zone.
5.  **Phase V: Methodological Local FSI**
    - High-fidelity 3D FSI simulations used as a validation centerpiece for the reduced-order pipeline.

## Software Ecosystem

| Tool | Primary Role |
|------|--------------|
| **Abaqus** | High-fidelity structural reference, contact benchmarking, and high-resolution automated batches. |
| **Kratos Multiphysics** | Main development environment, structural ROM, 1D fluid solver, and co-simulation framework. |
| **MATLAB** | Rapid prototyping, hyperelastic material testing, and preliminary data generation. |

## Modeling Philosophy: Multifidelity Pipeline

1.  **Reference Truth**: High-fidelity FEM simulations establish physical trust.
2.  **Compressed Reality**: ROMs transfer this truth into a computationally efficient environment.
3.  **Design Speed**: Manifold surrogates enable rapid evaluation and optimization of flow rates and hemolysis risk.

## Clinical Benchmarks

| Parameter | Representative Range / Limit |
|-----------|------------------------------|
| Adult Flow Rate | 2 – 7 L/min |
| Pressure Rise (Head) | 200 – 300 mmHg |
| Venous Suction Limit | -70 mmHg (Alarm threshold) |
| Arterial Return Limit | 400 mmHg (Alarm threshold) |
| Cannula Diameter | 15-17 Fr (Arterial), 21-24 Fr (Venous) |
| Circuit Volume | ~0.5 L (priming volume) |

## Technical Parameters

The following parameters are established based on the experimental configurations described in the reference papers (Rubio et al., 2025/2026) and the project email:

### Compliant Tube (Silicon/Latex/Rubber)
| Parameter | Value |
|-----------|-------|
| Diameter ($d_{ct}$) | 20 mm |
| Length ($l_{ct}$) | 100 mm |
| Thickness ($t$) | ~2 mm |
| Pre-strain ($\epsilon_{axial}$) | 2% (Implemented symmetrically as $\pm 1$ mm) |
| Young's Modulus ($E$) | 1.1026 MPa |
| Poisson's Ratio ($\nu$) | 0.45 (Stable almost-incompressible limit) |
| Shear Modulus ($G$) | 0.38 MPa |
| Density ($\rho$) | 1040 kg/m³ |

### Actuation & Circuit
| Parameter | Value |
|-----------|-------|
| Actuator Width | 20 mm |
| Actuator Position ($\beta$) | 0.5 (Midpoint) |
| Length Ratio ($\lambda$) | $l_l / l_s \approx 4.5$ (Optimal) |
| Rigid Pipe Diameter ($d_{rt}$) | 16 - 20 mm |

## Resonant Pumping Physics

The system's performance is governed by the interaction of pressure waves and structural compliance. Key metrics used for benchmarking include:

1.  **Womersley Number ($Wo^2$)**: Evaluates the importance of viscous effects.
    $$Wo^2 = \frac{d_{rt}^2 \sqrt{\rho P_b}}{\mu l_l}$$
    - High $Wo^2 (> 80)$: Viscous effects are subdominant; semi-empirical models are accurate.
    - Low $Wo^2 (< 20)$: Viscous effects significantly reduce net flow.

2.  **Ideal Resonant Period ($T_{ic}$)**:
    $$T_{ic} = \sqrt{\frac{2 V_{ct} l_s}{A_{rt} g h}}$$

3.  **Maximum Net Flow Rate ($Q_{ic}$)**:
    $$Q_{ic} = \sqrt{\frac{V_{ct} A_{rt} g h}{8 l_s}}$$

---
*For more details, refer to the documentation in the `References/` directory.*
