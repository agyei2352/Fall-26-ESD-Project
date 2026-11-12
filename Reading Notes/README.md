# Engineering Reading Notes

This document summarizes the core technical standards, manufacturer specifications, and design literature informing the smart ESD wristband monitor.

---

## 1. ANSI/ESD S20.20 & IEC 61340-5-1 (ESD Control Programs)
- **Standard:** ANSI/ESD S20.20-2021: *Protection of Electrical and Electronic Parts, Assemblies and Equipment*.
- **Key Concepts:**
  - Standard wrist strap system resistance requirement: **$< 3.5 \times 10^7\,\Omega$ ($35\text{ M}\Omega$)** for total person-to-ground resistance.
  - Recommended minimum series safety resistance: **$1.0 \times 10^6\,\Omega$ ($1\text{ M}\Omega$)** to limit current in case of accidental contact with commercial AC mains (120/240 VAC).
  - Continuous monitoring vs. periodic testing: Continuous monitoring provides real-time detection of intermittent failures, loose wristband fit, and broken grounding coil cords that periodic testing stations miss.
- **Project Application:** Sets the **$35\text{ M}\Omega$ upper limit for Warning/Fail** and justifies the **$1.0\text{ M}\Omega$ series current limit resistor** ($R_{\text{limit}}$) on the pulse drive line.

---

## 2. Nordic Semiconductor nRF52840 Product Specification (v1.11 / v1.12)
- **Section 7.3: Circuit Configuration No. 2 (QIAA aQFN-73):**
  - **Normal Voltage Mode:** When supply voltage is between $1.7\text{ V}$ and $3.6\text{ V}$ (e.g. 3.0 V CR2032), `VDDH` must be connected directly to `VDD`. REG0 is bypassed.
  - **DC/DC Converter:** Enabling REG1 DC/DC reduces active run currents from $\sim 7\text{ mA}$ to $\sim 3.3\text{ mA}$. Requires a $10\,\mu\text{H}$ inductor ($L_2$) between `DCC` (Pin B3) and `DEC4_6`.
  - **Mandatory Silicon Bridge:** Pins `DEC4` (Pin B5) and `DEC6` (Pin E24) must be connected together externally on the PCB with a $1.0\,\mu\text{F}$ capacitor ($C_4$) to ground.
- **Section 6.20: Successive Approximation ADC (SAADC):**
  - Acquisition time: Configurable from $3\,\mu\text{s}$ to $40\,\mu\text{s}$.
  - Maximum source impedance recommendation: $<800\text{ k}\Omega$ at $40\,\mu\text{s}$ acquisition. High source impedances ($>1\text{ M}\Omega$) introduce sample capacitor charging offset without extended settle/acquisition timing.
  - Internal reference: $0.6\text{ V}$ bandgap, with selectable gains ($1/6, 1/5, 1/4, 1/3, 1/2, 1, 2, 4$). Gain $1/6$ yields a $3.6\text{ V}$ full-scale range.
- **Project Application:** Governs the entire KiCad schematic, decoupling topology, crystal selection, and ADC sampling configuration.

---

## 3. Lithium Coin Cell Characteristics (CR2032)
- **Manufacturer Technical Handbooks (Panasonic / Energizer):**
  - Nominal voltage: $3.0\text{ V}$; nominal capacity: $\sim 225\text{ mAh}$ at $0.2\text{ mA}$ continuous discharge.
  - Internal resistance ($R_{\text{int}}$): $10\text{--}30\,\Omega$ fresh, increasing to $100\text{--}200\,\Omega$ near end-of-life.
  - Pulse discharge limitation: Continuous current should stay below $3\text{ mA}$; pulse current should stay below $15\text{ mA}$. Pulses causing high peak currents drop cell terminal voltage ($V = V_{\text{cell}} - I_{\text{pulse}} \cdot R_{\text{int}}$).
- **Project Application:** Validates the $1.25\text{ s}$ low-power duty cycle ($<2\,\mu\text{A}$ sleep, $1.8\text{ mA}$ LED blink) and mandates keeping the buzzer in Phase 2 to prevent brownout below the nRF52840's $1.7\text{ V}$ minimum operating voltage.
