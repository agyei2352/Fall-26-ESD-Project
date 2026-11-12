# Project Requirements & Verification Criteria

This document records the system engineering requirements, operational constraints, and verification results for the wearable dual-wire ESD wristband monitor.

---

## 1. Stage 1 Requirements Verification Status

- [x] **Software Models & Mechanical Design:** Completed MATLAB numerical analysis, Multisim SPICE pulse simulation, Wokwi logic verification, KiCad 10 PCB layout, and SolidWorks 3D mechanical enclosure.
- [x] **KiCad Schematic & PCB Layout:** Completed 2-layer PCB layout using official Nordic aQFN-73 reference geometry; verified with 0 ERC errors, 0 DRC shorts, and 0 clearance violations.
- [x] **Intended Use & User Specification:** Wearable ESD wrist strap continuous integrity monitor for electronics assembly technicians working in EPA (ESD Protected Areas) per ANSI/ESD S20.20 and IEC 61340-5-1.
- [x] **Dual-Wire Sensing & Grounding Concept:** High-impedance loop measurement ($V_{\text{pulse}} \to R_{\text{limit}} \to \text{Contact A} \to \text{Skin} \to \text{Contact B} \to R_{\text{ground}} \to \text{GND}$) with dedicated earth ground return cord to bench reference.
- [x] **Status Indication Logic:** Three discrete SMD LEDs (Green = Good, Yellow = Warning, Red = Fail) mapped to ANSI/ESD resistance criteria.
- [x] **Blink & Sleep Power Profile:** Implemented $250\text{ ms}$ active measurement window, $200\text{ ms}$ LED indicator pulse, and $800\text{ ms}$ ultra-low-power sleep interval ($1.25\text{ s}$ total cycle).
- [x] **Low-Power Nordic Sleep:** Designed around ARM Cortex-M4F `System ON - IDLE` ($<2.0\,\mu\text{A}$) with $32.768\text{ kHz}$ low-power crystal oscillator.
- [x] **Phase 1 Baseline Hardware:** Buzzer strictly deferred to Phase 2 to preserve CR2032 peak-current margin.
- [x] **Form Factor & Size Targets:** Board constrained to $32.0 \times 40.0\text{ mm}$; enclosure constrained to $36.6 \times 44.6 \times 12.1\text{ mm}$ with $20\text{ mm}$ strap lugs.
- [x] **Electrical Safety Constraints:** $1.0\text{ M}\Omega$ current-limiting series resistor guarantees operator fault current $< 3.0\,\mu\text{A}$ in all failure modes.
- [x] **Power Architecture & Battery Safety:** CR2032 Lithium primary coin cell ($3.0\text{ V}$ nominal). No charging circuit; USB charging is prohibited.
- [x] **Waveform Dynamics & Settling Characterization:** Modeled pulse edge, settled plateau, edge drop, and $5\%$ settling times across 4 representative RC scenarios.

---

## 2. Project Stages & Gates

### Stage 1: Software and Design Readiness (COMPLETE)
- **MATLAB Analysis:** Full analytical calculation report, transfer curves, and CSV feature data.
- **Multisim SPICE Simulation:** Circuit netlist, dual-channel oscilloscope transient capture, and probe voltages.
- **Wokwi Firmware Proxy:** Logic verification, potentiometer test matrix, and LED switching state machine.
- **Arduino / Nordic Firmware:** State machine timing, pin aliases, and ADC resistance conversion equations.
- **KiCad 10 PCB CAD:** 2-layer layout on bare nRF52840-QIAA, ERC/DRC verification reports, and 3D renders.
- **SolidWorks Mechanical CAD:** 3D printable top shell, bottom cradle with strap lugs, battery door, and assembly.

### Stage 2: Physical Prototype & Hardware Validation (PENDING REVIEW GATE)
- Component procurement using the [Bill of Materials](../Parts%20List/README.md).
- PCB fabrication and SMT assembly of bare nRF52840-QIAA prototypes.
- Bench validation of loaded CR2032 voltage sag and SAADC sampling error via test points `TP1`--`TP4`.
- Comparison of physical oscilloscope measurements against MATLAB/Multisim models.

---

## 3. Resistance Classification Thresholds

The monitor classifies skin-to-ground loop resistance into three standard operational bands:

| Resistance Range | Equivalent ADC Sense Voltage | Operating Status | Visual Indicator | Meaning / Operator Action |
| :--- | :--- | :--- | :--- | :--- |
| **$< 5.0\text{ M}\Omega$** | **$> 0.4286\text{ V}$** | **GOOD** | Green LED | Wristband contact and ground path are optimal. Normal operation. |
| **$5.0\text{ M}\Omega\text{ to }35.0\text{ M}\Omega$** | **$0.0811\text{ V to }0.4286\text{ V}$** | **WARNING** | Yellow LED | Marginal contact or dry skin. Adjust strap fit or apply moisturizing lotion. |
| **$> 35.0\text{ M}\Omega$** | **$< 0.0811\text{ V}$** | **FAIL** | Red LED | Unacceptable resistance or open circuit. ESD protection compromised. |
| **Open Circuit** | **$\le 0.0200\text{ V}$** | **FAIL (OPEN)** | Red LED | Ground cord detached or wristband removed. |

---

## 4. Electrical Architecture Summary

- **Core SoC:** Bare **Nordic nRF52840-QIAA (aQFN-73)** running in Normal Voltage Mode ($VDD = VDDH = 3.0\text{ V}$).
- **Power Source:** Single CR2032 Lithium coin cell ($3.0\text{ V}$ nominal, $225\text{ mAh}$).
- **Regulators:** REG0 bypassed, internal REG1 DC/DC buck converter active with $10\,\mu\text{H}$ inductor.
- **RF Transceiver:** On-board inverted-F PCB antenna with $50\,\Omega$ Pi-match network ($L_1 = 3.9\text{ nH}, C_{12} = 1.2\text{ pF}, C_{13} = 1.5\text{ pF}$). Radio transmission disabled during Stage 1 baseline to minimize current draw.
- **Sensing Interface:** Single-ended SAADC channel on pin `P0.02 / AIN0`, preceded by $1.0\text{ M}\Omega$ limit resistor and followed by $1.0\text{ M}\Omega$ ground return resistor.
