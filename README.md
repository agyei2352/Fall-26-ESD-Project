# Wearable Smart ESD Wristband Monitor (Stage 1)

> [!NOTE]
> ### Engineering Portfolio & Technical Archive Notice
> **Development Context:** This project was engineered, modeled, and verified prior to publication as an academic/R&D milestone at the University of North Texas.  
> **Toolchain:** Primary development, embedded firmware scripting, and project integration were executed locally in **VS Code**, alongside native engineering design suites (**KiCad 10**, **SolidWorks**, **NI Multisim 14.3**, and **MATLAB**).  
> **Repository Purpose:** This repository serves as an **external public portfolio and verification archive** for engineering recruiters, hiring managers, and interviewers to inspect the design files, source code, schematics, 3D CAD models, and simulation data.

---

## Project Overview

A wearable, continuous dual-wire ESD (Electrostatic Discharge) wristband integrity monitor engineered around a bare **Nordic Semiconductor nRF52840-QIAA (aQFN-73)** System-on-Chip and powered by a single **CR2032 primary coin cell** ($3.0\text{ V}$ nominal).

The device measures human skin contact impedance and wristband loop continuity in real-time to prevent ESD damage in sensitive semiconductor and medical device cleanroom environments according to **ANSI/ESD S20.20** specifications.

```
+-----------------------------------------------------------------------------------------+
|                               SYSTEM ARCHITECTURE DIAGRAM                               |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|   +-------------------+       +-----------------------+       +---------------------+   |
|   |  CR2032 Coin Cell | ----> | Nordic nRF52840 SoC   | ----> | Status LEDs / User  |   |
|   |  (3.0V, 225 mAh)  |       | (Arm Cortex-M4, BLE)  |       | (Good, Warn, Fail)  |   |
|   +-------------------+       +-----------------------+       +---------------------+   |
|                                       ^       |                                         |
|                                       |       v                                         |
|                             ADC Sense |       | Active Pulse                            |
|                                       |       | (P0.13)                                 |
|                               +-----------------------+                                 |
|                               | Dual-Wire ESD Strap   |                                 |
|                               | & Human Skin Divider  |                                 |
|                               +-----------------------+                                 |
+-----------------------------------------------------------------------------------------+
```

---

## Key Hardware & Engineering Specifications

- **Microcontroller / SoC:** Bare Nordic Semiconductor **nRF52840-QIAA (aQFN-73)** running at $64\text{ MHz}$ Arm Cortex-M4F with $1\text{ MB}$ Flash and $256\text{ KB}$ RAM.
- **Power Budget & Battery Life:** Powered by a Keystone 3002 retainer with a single CR2032 cell. Ultra-low power duty cycle ($250\text{ ms}$ active measurement, $800\text{ ms}$ system sleep at $<2\,\mu\text{A}$), enabling continuous multi-month operation.
- **PCB Layout (KiCad 10):** Custom 2-layer board ($32.0 \times 40.0\text{ mm}$), $1.6\text{ mm}$ FR4, $1\text{ oz}$ copper. Includes matched RF trace geometry, $32\text{ MHz}$ HFXO / $32.768\text{ kHz}$ LFXO reference crystals, SWD programming header, and a high-impedance $1\text{ M}\Omega$ active pulse / sense divider path. Achieved **0 ERC errors** and **0 DRC violations**.
- **Mechanical Enclosure (SolidWorks):** Parametric wearable housing ($36.6 \times 44.6 \times 12.1\text{ mm}$) featuring $20\text{ mm}$ strap lugs, toolless twist-lock battery door, and $\varnothing 2\text{ mm}$ optical light-pipe guides. Validated zero-collision fit via 3D STEP import.

---

## Operating Resistance Bands & Detection Logic

Continuous status classification is derived via an active pulse voltage divider sampled by the nRF52840 SAADC:

$$\text{ADC Voltage } V_{\text{sense}} = V_{\text{pulse}} \times \frac{R_{\text{ref}}}{R_{\text{ref}} + R_{\text{loop}}}$$

| Status Band | Measured Loop Resistance ($R_{\text{loop}}$) | Sense Voltage ($V_{\text{sense}}$) | Indicator Behavior | Physical Condition |
| :--- | :--- | :--- | :--- | :--- |
| **GOOD** | $< 5.0\text{ M}\Omega$ | $> 0.4286\text{ V}$ | Green LED active | Proper strap fit and skin contact |
| **WARNING** | $5.0\text{ M}\Omega \text{ to } 35.0\text{ M}\Omega$ | $0.0811\text{ V to } 0.4286\text{ V}$ | Yellow LED active | Dry skin, high impedance, loose fit |
| **FAIL** | $> 35.0\text{ M}\Omega$ | $< 0.0811\text{ V}$ | Red LED active | Open loop, disconnected strap, ungrounded |

---

## Repository Directory Structure

```text
smart-esd-wristband-monitor/
├── Arduino Code/                # Bare nRF52840 state machine & firmware (VS Code)
│   ├── ESD_Wristband_Firmware.ino
│   ├── firmware_timing_state_machine.png
│   └── README.md
├── Digital Circuit Data/        # NI Multisim 14.3 circuit, SPICE netlist, oscilloscope captures
│   ├── ESD Impedance Device.ms14
│   ├── ESD_Wristband_Multisim_Circuit.cir
│   ├── multisim_circuit_schematic.png
│   ├── multisim_oscilloscope_transient.png
│   └── README.md
├── MATLAB Model/                # Mathematical model, RC transient response, transfer curves
│   ├── esd_wristband_status_model.m
│   ├── ESD_Wristband_Calculation_Report.pdf
│   ├── matlab_pulse_response_plot.png
│   ├── matlab_adc_transfer_curve.png
│   └── README.md
├── PCB Design/                  # Native KiCad 10 project, 2-layer PCB layout, 3D renders, DRC
│   ├── ESD_Wristband_Monitor.kicad_pro / .kicad_sch / .kicad_pcb
│   ├── ESD_Wristband_Monitor.step
│   ├── board_render_3d.png
│   ├── board_render_top.png
│   ├── erc_report.rpt (0 Errors, 0 Warnings)
│   ├── drc_report.rpt (0 Shorts, 0 Clearance Errors)
│   └── README.md
├── SolidWorks Design/           # 3D printable mechanical enclosure, strap lugs, and battery bay
│   ├── Complete_Enclosure_Assembly.stl  (Viewable in GitHub 3D viewer)
│   ├── Enclosure_Top_Cover.stl
│   ├── Enclosure_Bottom_Base.stl
│   ├── Battery_Door.stl
│   ├── ESD_Wristband_Monitor_PCB.step
│   └── README.md
├── Wokwi/                       # Interactive firmware logic verification & sweep data
│   ├── sketch.ino
│   ├── wokwi_wiring_diagram.png
│   └── README.md
├── Parts List/                  # Stage 1 BOM with MPNs and footprints
│   └── README.md
├── Project Requirements/        # ANSI/ESD S20.20 standards and specifications
│   └── README.md
├── Test Results/                # Verification logs and potentiometer sweep matrices
│   └── README.md
└── Stage 1 Plan and Learning Resources.md # Engineering plan and Stage 2 hardware roadmap
```

---

## Stage 1 Verification & Testing Matrix

| Tool / Environment | Engineering Role | Key Output / Verification Metric | Visual Asset |
| :--- | :--- | :--- | :--- |
| **VS Code / Arduino** | State machine firmware & timing control | $250\text{ ms}$ pulse / $800\text{ ms}$ sleep state cycle | [`firmware_timing_state_machine.png`](Arduino%20Code/firmware_timing_state_machine.png) |
| **KiCad 10** | Schematic capture & 2-layer PCB layout | Passed ERC (0 errors) and DRC (0 violations) | [`board_render_3d.png`](PCB%20Design/board_render_3d.png) |
| **SolidWorks** | Enclosure CAD & 3D print validation | Zero-collision assembly mating via STEP | [`SolidWorks Design/`](SolidWorks%20Design/README.md) |
| **MATLAB** | Mathematical RC transient modeling | Calculated $V_{\text{plateau}}$, $\tau$, and settling curve | [`matlab_pulse_response_plot.png`](MATLAB%20Model/matlab_pulse_response_plot.png) |
| **NI Multisim** | SPICE circuit simulation | Verified node voltage transient response | [`multisim_circuit_schematic.png`](Digital%20Circuit%20Data/multisim_circuit_schematic.png) |
| **Wokwi** | Hardware logic prototype sweep | Verified Good/Warning/Fail transitions | [`wokwi_wiring_diagram.png`](Wokwi/wokwi_wiring_diagram.png) |

---

## How to Review & Inspect Files

- **View 3D Enclosure:** Click on [`SolidWorks Design/Complete_Enclosure_Assembly.stl`](SolidWorks%20Design/Complete_Enclosure_Assembly.stl) to inspect the 3D model directly in GitHub's native 3D browser viewer.
- **Inspect Firmware:** Open [`Arduino Code/ESD_Wristband_Firmware.ino`](Arduino%20Code/ESD_Wristband_Firmware.ino) to review the bare nRF52840 register configuration, SAADC sampling, and sleep timing logic.
- **Inspect PCB Design:** Open `PCB Design/ESD_Wristband_Monitor.kicad_pro` using **KiCad 10** to view schematic sheets, design rules, and copper routing.
- **Review Circuit SPICE Simulation:** Open `Digital Circuit Data/ESD Impedance Device.ms14` in **NI Multisim 14.3** or inspect the netlist in `Digital Circuit Data/ESD_Wristband_Multisim_Circuit.cir`.

---

## License & Intellectual Property

Copyright &copy; 2026 Prince Agyei. All Rights Reserved.  
This project and all associated design assets (firmware, schematics, PCB layouts, 3D CAD models, and simulation files) are published strictly for recruiter portfolio review and academic verification. Unauthorized copying, physical fabrication, modification, or commercial distribution is prohibited. See [`LICENSE`](LICENSE) for complete terms.
