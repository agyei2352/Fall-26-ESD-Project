# Stage 1 KiCad PCB Design Proposal and Open Review Items

## 1. Executive Summary & Design Scope

This document provides the Stage 1 schematic architecture, component bill of materials (BOM), reference design verification, and open design review items for the **wearable ESD wristband monitor**.

### Key System Parameters
- **Target MCU:** Bare **Nordic Semiconductor nRF52840-QIAA** (aQFN-73 package, 7.0 × 7.0 mm, 0.5 mm pitch). Not a module, XIAO, or development board.
- **Power Supply:** Single **CR2032 primary lithium coin cell** (nominal 3.0 V, 220–240 mAh). **No charger IC or USB charge path.**
- **Regulator Mode:** **Normal Voltage Mode** (1.7 V to 3.6 V operating range). VDD and VDDH pins shorted together; REG0 bypassed; REG1 DC/DC buck converter components provisioned to minimize active peak currents.
- **Measurement Network (Phase 1):**
  $$\text{3.0 V Pulse (P0.13)} \longrightarrow R_{\text{limit}} (1\text{ M}\Omega) \longrightarrow \text{Contact A} \longrightarrow [R_{\text{skin}} \parallel C_{\text{skin}}] \longrightarrow \text{Contact B / ADC Sense} \longrightarrow R_{\text{ground}} (1\text{ M}\Omega) \longrightarrow \text{MCU GND / Earth Ground}$$
- **Status Indicators:** Three low-current LEDs (Good: Green, Warning: Yellow, Fail: Red), pulsed for 200 ms per 1.25 s cycle.
- **Audible Alert (Buzzer):** Excluded from Phase 1 baseline (Phase 2 feature, pending coin-cell peak-current validation).
- **Programming & Test Access:** SWD pads/header (SWDIO, SWDCLK, RESET, VDD, GND) and dedicated test points for Pulse, Sense, VDD, and GND.

---

## 2. Nordic Reference Material & Design Provenance

The design directly adopts the reference circuitry and layout recommendations from official Nordic Semiconductor documentation:

1. **Nordic Semiconductor nRF52840 Product Specification:**
   - **Document Version:** v1.11 / v1.12, Chapter 7: *Hardware and layout* -> Section 7.3: *Reference circuitry*.
   - **Specific Topology:** *Circuit Configuration No. 2 for QIAA aQFN73* (Normal Voltage Mode with internal DC/DC buck converter for REG1 enabled, USB disabled).
   - **Silicon Package:** QIAA (73-pin aQFN, $7 \times 7\text{ mm}$, $0.5\text{ mm}$ pitch).
   - **KiCad 10 Library Symbol:** `MCU_Nordic:nRF52840`
   - **KiCad 10 Library Footprint:** `Package_DFN_QFN:Nordic_AQFN-73-1EP_7x7mm_P0.5mm`

2. **Official Reference Layout & Hardware Design Files:**
   - **Source Archive:** Nordic Semiconductor `nRF52840-QIAA Reference Layout v1.3` (PCA10056 reference materials).
   - **RF Implementation:** Single-ended $50\,\Omega$ output on pin `ANT` (H23) with discrete Pi-network matching ($L_1 = 3.9\text{ nH}$, $C_{12} = 1.2\text{ pF}$, $C_{13} = 1.5\text{ pF}$) transitioning to a $50\,\Omega$ coplanar transmission line and integrated PCB trace antenna with recommended ground clearance.
   - **Decoupling Rules:** Dedicated ceramic decoupling capacitors on every VDD pin, bulk 4.7 µF on battery input, $100\text{ nF}$ on `DEC1`, $100\text{ pF}$ on `DEC3`, and $1.0\,\mu\text{F}$ on `DEC4` externally tied to `DEC6`.

---

## 3. Proposed Schematic Architecture & Pin Map

### 3.1 SoC Pin Allocation

| Pin # | Pin Name | Net Name | Function / Description |
| :--- | :--- | :--- | :--- |
| **A12** | `AIN0 / P0.02` | `ADC_SENSE` | Analog input to SAADC from Contact B / Rground sense node |
| **AD8** | `P0.13` | `PULSE_DRIVE` | 3.0 V pulse driver output to 1 MΩ limit resistor |
| **AC9** | `P0.14` | `LED_GOOD` | Digital output driving Green LED (Good: $R < 5\text{ M}\Omega$) |
| **AD10** | `P0.15` | `LED_WARN` | Digital output driving Yellow LED (Warning: $5\text{ M}\Omega \le R \le 35\text{ M}\Omega$) |
| **AC11** | `P0.16` | `LED_FAIL` | Digital output driving Red LED (Fail: $R > 35\text{ M}\Omega$ or open) |
| **AA24** | `SWDCLK` | `SWDCLK` | ARM SWD Serial Wire Clock for programming/debugging |
| **AC24** | `SWDIO` | `SWDIO` | ARM SWD Serial Wire Data Input/Output |
| **AC13** | `P0.18 / ~RESET`| `~RESET` | Hardware Reset / Configurable GPIO with pull-up pad |
| **B24** | `XC1` | `HFXO_XC1` | 32.0 MHz Crystal Oscillator input |
| **A23** | `XC2` | `HFXO_XC2` | 32.0 MHz Crystal Oscillator output |
| **D2** | `XL1 / P0.00` | `LFXO_XL1` | 32.768 kHz Low-frequency Crystal input |
| **F2** | `XL2 / P0.01` | `LFXO_XL2` | 32.768 kHz Low-frequency Crystal output |
| **H23** | `ANT` | `RF_ANT` | 2.4 GHz RF Transceiver single-ended output to matching network |
| **B3** | `DCC` | `DCC_SW` | Internal DC/DC converter switching pin (to L2 $10\,\mu\text{H}$) |
| **B5** | `DEC4` | `DEC4_6` | 1.3 V Digital Core LDO/DC-DC output (tied directly to DEC6) |
| **E24** | `DEC6` | `DEC4_6` | 1.3 V Radio supply decoupling (externally tied to DEC4) |
| **C1** | `DEC1` | `DEC1` | 1.1 V Core supply decoupling ($100\text{ nF}$ to GND) |
| **D23** | `DEC3` | `DEC3` | High-frequency power supply bypass ($100\text{ pF}$ to GND) |
| **A18** | `DEC2` | `N.C.` | Left unconnected per Normal Voltage Mode reference |
| **N24** | `DEC5` | `N.C.` | Left unconnected per reference |
| **AB2** | `DCCH` | `N.C.` | Not used in Normal Voltage Mode |
| **AC5** | `DECUSB` | `N.C.` | Not used (USB disabled) |
| **AD2** | `VBUS` | `GND` | Tied to GND per reference when USB is unused |
| **AD4** | `D-` | `N.C.` | Left unconnected |
| **AD6** | `D+` | `N.C.` | Left unconnected |
| **B1, W1, A22, AD14, AD23** | `VDD` | `+3V0` | 3.0 V Power Supply from CR2032 battery |
| **Y2** | `VDDH` | `+3V0` | Shorted directly to `VDD` for Normal Voltage Mode |
| **B7, EP** | `VSS` | `GND` | System Ground (center exposed pad EP soldered to PCB GND) |
| **F23** | `VSS_PA` | `GND` | Power Amplifier ground return connected to solid GND |

---

## 4. Proposed Component Bill of Materials (BOM)

| Ref Des | Qty | Value / Part | Package | Manufacturer / MPN | Description / Application Notes |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **U1** | 1 | nRF52840-QIAA | aQFN-73 ($7\times 7\text{ mm}$) | Nordic Semi `nRF52840-QIAA-R` | Multi-protocol BLE/802.15.4 SoC |
| **BT1** | 1 | CR2032 Battery Holder | SMT / THM | Keystone 3002 (SMT) or 3003 (TH) | Retention clip for CR2032 3.0 V coin cell |
| **X1** | 1 | 32.000 MHz Crystal | 2016 / 3225 | Murata XR32M000 / Abracon ABM11 | HFXO Crystal, $\pm 10\text{ ppm}$, $C_L = 8\text{–}10\text{ pF}$ |
| **X2** | 1 | 32.768 kHz Crystal | 3215 / 2012 | Abracon ABS07 / Epson FC-135 | LFXO Crystal, $\pm 20\text{ ppm}$, $C_L = 9\text{ pF}$ |
| **C1, C2** | 2 | 12 pF | 0402 | Murata GRM1555C1H120JA01D | NP0/C0G $\pm 5\%$, HFXO load capacitors |
| **C14, C15** | 2 | 12 pF | 0402 | Murata GRM1555C1H120JA01D | NP0/C0G $\pm 5\%$, LFXO load capacitors |
| **C_bulk** | 1 | 4.7 µF | 0603 | Murata GRM188R60J475KE19D | X5R 6.3 V $\pm 10\%$, battery bulk filter |
| **C5, C7–C11** | 6 | 100 nF | 0402 | Murata GRM155R71C104KA88D | X7R 16 V $\pm 10\%$, VDD and DEC1 bypass |
| **C3** | 1 | 100 pF | 0402 | Murata GRM1555C1H101JA01D | NP0/C0G 50 V, DEC3 high-frequency bypass |
| **C4** | 1 | 1.0 µF | 0402 / 0603 | Murata GRM155R60J105KE19D | X5R 6.3 V, DEC4/DEC6 regulator filter |
| **L1** | 1 | 3.9 nH | 0402 | Murata LQW15AN3N9B00D | High-Q wirewound inductor, RF match |
| **C12** | 1 | 1.2 pF | 0402 | Murata GJM1555C1H1R2BB01D | NP0/C0G $\pm 0.1\text{ pF}$, RF matching shunt |
| **C13** | 1 | 1.5 pF | 0402 | Murata GJM1555C1H1R5BB01D | NP0/C0G $\pm 0.1\text{ pF}$, RF matching shunt |
| **L2** | 1 | 10 µH | 0603 | Murata LQM21PN100MGHD | DC/DC inductor, $I_{sat} \ge 50\text{ mA}$ (REG1) |
| **R_limit** | 1 | 1.00 MΩ | 0603 / 0805 | Vishay MCT06030C1004FP500 | Precision resistor, 1% tolerance, 50 V |
| **R_ground**| 1 | 1.00 MΩ | 0603 / 0805 | Vishay MCT06030C1004FP500 | Precision resistor, 1% tolerance, 50 V |
| **R1, R2, R3**| 3 | 1.50 kΩ | 0402 | Panasonic ERJ-2RKF1501X | LED current limiting, 1% (sets $I_{LED} \approx 0.8\text{ mA}$) |
| **D_GOOD** | 1 | Green LED | 0603 | Lite-On LTST-C190GKT | High-efficiency 525 nm Green LED |
| **D_WARN** | 1 | Yellow LED | 0603 | Lite-On LTST-C190YKT | High-efficiency 590 nm Yellow LED |
| **D_FAIL** | 1 | Red LED | 0603 | Lite-On LTST-C190KRKT | High-efficiency 630 nm Red LED |
| **J1** | 1 | Contact Pad A | SMT Snap / Pad | Custom / Keystone 82 | Snap terminal to conductive nylon contact A |
| **J2** | 1 | Contact Pad B | SMT Snap / Pad | Custom / Keystone 82 | Snap terminal to conductive nylon contact B |
| **J3** | 1 | Ground Cord Pad | SMT Snap / Pad | Custom / Keystone 82 | External ground cord connection to system GND |
| **J_SWD** | 1 | 5-Pin SWD Header | 1.27 mm / Pad array | Harwin / Tag-Connect TC2030 | Programming/debug interface (VDD, SWDIO, SWDCLK, RESET, GND) |
| **TP1–TP4** | 4 | Test Points | SMT Test Pad | Keystone 5015 / SMT Pad | TP_PULSE, TP_SENSE, TP_VDD, TP_GND |

---

## 5. Unresolved Electrical and Mechanical Inputs (Review Gate)

Per project guidelines, the following critical decisions remain **open** and are marked for engineering review prior to fabrication release:

### 5.1 SAADC Interface: Buffer, Protection, and Source Impedance
1. **Source Impedance & Sampling Settling:**
   - The Thevenin equivalent resistance seen by the SAADC input node is:
     $$R_{\text{source}} = R_{\text{ground}} \parallel (R_{\text{skin}} + R_{\text{limit}}) \approx 0.857\text{ M}\Omega \text{ (at } 5\text{ M}\Omega) \text{ to } 1.000\text{ M}\Omega \text{ (at open circuit)}$$
   - Nordic’s nRF52840 specification recommends $R_{\text{source}} \le 800\text{ k}\Omega$ when configured for maximum acquisition time ($40\,\mu\text{s}$). An unbuffered $1.0\text{ M}\Omega$ source requires validating that the internal sampling capacitor ($C_{\text{sample}} \approx 2.5\text{ pF}$) is sufficiently charged or that multiple consecutive conversions avoid charge redistribution errors.
2. **Buffer Candidate Trade-offs:**
   - Candidate nano-power op amps (e.g., TI LPV811, Microchip MCP6041, TI OPA333) offer ultra-low supply currents ($300\text{–}450\text{ nA}$), but present critical constraints:
     - **Common-Mode Input Headroom:** At discharged battery levels ($V_{DD} \approx 2.0\text{ V}$), some low-power op amps lose rail-to-rail linear performance near the upper or lower supply rail.
     - **Input Bias / Leakage Current:** At high ambient temperatures, input leakage current ($I_{\text{bias}} > 1\text{ nA}$) flowing through $1\text{ M}\Omega$ introduces tens of millivolts of offset, corrupting the $40\text{ M}\Omega$ plateau measurement.
     - **Protection Leakage:** External TVS diodes or clamping diodes on Contact B must have sub-nanoamp reverse leakage at $1.5\text{ V}$ to avoid distorting the voltage divider.
3. **Phase 1 Decision:** Retain the passive direct connection to `AIN0/P0.02` with accessible test pads (`TP_SENSE`). Mark active buffering and clamp diodes as an open design review item pending physical bench characterization.

### 5.2 CR2032 Loaded-Voltage and Peak-Current Margin
1. **Pulse Current vs. Battery Internal Resistance:**
   - A standard CR2032 has an internal resistance of $R_{\text{cell}} \approx 10\text{–}20\,\Omega$ when fresh, increasing to $40\text{–}100\,\Omega$ as capacity discharges below 50%.
   - **Load Breakdown:**
     - Measurement pulse current: $I_{\text{pulse}} \le 3.0\text{ V} / 2\text{ M}\Omega = 1.5\,\mu\text{A}$ (negligible).
     - Indicator LED current: $I_{\text{LED}} \approx 0.8\text{–}1.0\text{ mA}$ for $200\text{ ms}$.
     - CPU active current (64 MHz): $I_{\text{CPU}} \approx 3.0\text{–}4.5\text{ mA}$.
     - Radio peak current: If enabled at 0 dBm with DC/DC, $I_{\text{radio}} \approx 4.8\text{ mA}$; without DC/DC, $\approx 10\text{ mA}$; at $+8\text{ dBm}$, $\approx 14.8\text{ mA}$.
   - **Instantaneous Voltage Sag:**
     - Under a $5\text{ mA}$ active spike (CPU + LED) on a partially depleted cell ($R_{\text{cell}} = 40\,\Omega$):
       $$\Delta V_{\text{drop}} = 5\text{ mA} \times 40\,\Omega = 0.20\text{ V}$$
     - If the unloaded cell is at $2.2\text{ V}$, loaded $V_{DD}$ drops to $2.0\text{ V}$, maintaining margin above the $1.7\text{ V}$ brownout reset threshold.
     - However, simultaneous radio transmission ($15\text{ mA}$) would drop the rail by $0.6\text{ V}$, risking brownout.
2. **Phase 1 Decision:** The radio is disabled in Stage 1 firmware. The $4.7\,\mu\text{F}$ bulk capacitor provides energy buffering during the 200 ms LED blink. Validate loaded battery voltage sag on bench hardware across cell discharge curves before committing to wireless transmission.

### 5.3 Mechanical Envelope & Wristband Integration
1. **Enclosure Fit:** SolidWorks CAD modeling is pending; final PCB outline (e.g. $24 \times 32\text{ mm}$ or rounded oval) must accommodate the Keystone 3002 coin cell holder ($20\text{ mm}$ diameter footprint) and the Nordic RF antenna keepout.
2. **Contact Attachment:** Physical attachment of conductive nylon bands A & B (SMD snap studs vs. soldered stranded flex leads) must be finalized with the mechanical team.
3. **RF Antenna Orientation:** The antenna must be located along the top edge of the PCB, directed away from the skin contact plane to minimize human body absorption and detuning.

---

## 6. KiCad Implementation Strategy (Stage 3 & 4 Preview)

Following review approval:
1. **Native Project & Schematic Generation:** Create `ESD_Wristband_Monitor.kicad_pro` and `ESD_Wristband_Monitor.kicad_sch` with all library-backed symbols (`MCU_Nordic:nRF52840`, passives, LEDs, test points) and structured nets.
2. **Board Layout (`.kicad_pcb`):**
   - Utilize KiCad 10 Python API (`pcbnew`) to load official footprints from `Package_DFN_QFN.pretty` and `Resistor_SMD.pretty`.
   - Place components with strict adherence to Nordic RF reference geometry:
     - $50\,\Omega$ coplanar waveguide from ANT pin through $L_1$, $C_{12}$, $C_{13}$ to antenna.
     - Decoupling capacitors immediately adjacent to corresponding VDD pins with via-in-pad or direct ground stitching.
     - `DEC4` connected to `DEC6` via low-inductance trace.
     - Exposed thermal ground pad (EP) stitched with ground vias to bottom ground plane.
     - High-impedance ADC sense path isolated from switching regulator and pulse driver traces.
3. **Verification & Outputs:**
   - Execute schematic ERC via `kicad-cli sch erc`.
   - Execute board DRC via `kicad-cli pcb drc`.
   - Render 3D board view via `kicad-cli pcb render`.
   - Save all artifacts, netlists, reports, and rendered images directly in `C:\Fall 26 ESD Project\PCB Design\`.

