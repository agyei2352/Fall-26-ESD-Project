# Parts List

Track component name, quantity, key specifications, manufacturer or supplier, part number, estimated cost, and selection notes.

## Stage 1 Bill of Materials (Nordic nRF52840-QIAA Baseline)

| Item | Qty | Selection / specification | Manufacturer / part | Package | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| **MCU** | 1 | Bare nRF52840 SoC | Nordic Semiconductor `nRF52840-QIAA-R` | aQFN-73 ($7\times 7\text{ mm}$) | Primary SoC; support circuitry and RF layout per Nordic reference design. |
| **Primary battery** | 1 | CR2032 Lithium primary cell (3.0 V, 225 mAh) | Panasonic `CR2032` / Energizer `CR2032` | 20 mm coin cell | Primary non-rechargeable cell. Pulse-current sag and runtime to be verified. |
| **Battery holder** | 1 | CR2032 SMT retainer clip | Keystone `3002` | SMT coin cell clip | Matches 20 mm coin cell footprint. Enclosure fit pending SolidWorks review. |
| **Charging IC** | 0 | None (CR2032 is non-rechargeable) | N/A | N/A | No charging circuit. USB charging is strictly prohibited. |
| **Buzzer** | 0 | None in Phase 1 (Phase 2 feature) | N/A | N/A | Excluded from Phase 1 PCB to conserve CR2032 current margin. |
| **HFXO Crystal** | 1 | 32.000 MHz, $\pm 10\text{ ppm}$, $C_L = 8\text{–}10\text{ pF}$ | Murata `XR32M000` / Abracon `ABM11` | SMD 2016 / 3225 | Required for 2.4 GHz radio and high-speed clocking. |
| **LFXO Crystal** | 1 | 32.768 kHz, $\pm 20\text{ ppm}$, $C_L = 9\text{ pF}$ | Abracon `ABS07` / Epson `FC-135` | SMD 3215 | Low-power sleep clocking and accurate RTC timing. |
| **Crystal load caps** | 4 | 12 pF NP0/C0G $\pm 5\%$, 50 V | Murata `GRM1555C1H120JA01D` | 0402 | 2 for HFXO (C1, C2), 2 for LFXO (C14, C15). |
| **Bulk capacitor** | 1 | 4.7 µF X5R 6.3 V $\pm 10\%$ | Murata `GRM188R60J475KE19D` | 0603 | Battery supply bulk decoupling. |
| **VDD decoupling** | 6 | 100 nF X7R 16 V $\pm 10\%$ | Murata `GRM155R71C104KA88D` | 0402 | 5 for VDD pins, 1 for DEC1 regulator pin. |
| **HF bypass cap** | 1 | 100 pF NP0/C0G 50 V | Murata `GRM1555C1H101JA01D` | 0402 | DEC3 pin internal supply bypass. |
| **Core regulator cap**| 1 | 1.0 µF X5R 6.3 V $\pm 10\%$ | Murata `GRM155R60J105KE19D` | 0402 | DEC4/DEC6 1.3 V regulator stabilization. |
| **DC/DC inductor** | 1 | 10 µH, $I_{sat} \ge 50\text{ mA}$, $\pm 20\%$ | Murata `LQM21PN100MGHD` | 0603 | Internal REG1 DC/DC buck converter choke. |
| **RF match inductor** | 1 | 3.9 nH high-Q wirewound | Murata `LQW15AN3N9B00D` | 0402 | Single-ended RF matching element (L1). |
| **RF match caps** | 2 | 1.2 pF, 1.5 pF NP0/C0G $\pm 0.1\text{ pF}$ | Murata `GJM1555C1H1R2BB01D` / `GJM1555C1H1R5BB01D` | 0402 | RF matching shunt elements (C12, C13). |
| **Series limit resistor** | 1 | 1.00 MΩ, 1%, 0.1 W | Vishay `MCT06030C1004FP500` | 0603 / 0805 | Current limiter in wristband pulse path ($R_{limit}$). |
| **Return sense resistor**| 1 | 1.00 MΩ, 1%, 0.1 W | Vishay `MCT06030C1004FP500` | 0603 / 0805 | Ground return divider resistor ($R_{ground}$). |
| **LED series resistors**| 3 | 1.50 kΩ, 1%, 0.063 W | Panasonic `ERJ-2RKF1501X` | 0402 | Current limiting for Good, Warning, Fail LEDs (~0.8 mA). |
| **Status LEDs** | 3 | Green, Yellow, Red SMD LEDs | Lite-On `LTST-C190GKT` / `YKT` / `KRKT` | 0603 | Good, Warning, Fail status indicators. |
| **Wrist contacts** | 2 | Conductive contact snaps / pads | Keystone `82` / custom SMD snap | SMT | Terminals to conductive nylon wristband contacts A & B. |
| **Ground cord pad** | 1 | Snap connector / stud | Keystone `82` / custom SMD snap | SMT | Terminal for external ground reference lead. |
| **Programming header** | 1 | 5-pin SWD pad array / header | Tag-Connect `TC2030` or 1.27 mm pad array | SMD / Pogo | SWDCLK, SWDIO, RESET, VDD, GND. |
| **Test points** | 4 | Miniature SMD test pads | Keystone `5015` / copper pad | SMT | TP_PULSE, TP_SENSE, TP_VDD, TP_GND. |

## Open Design Review Decisions

1. **SAADC Input Buffer & Protection:** Direct passive connection is baseline. Buffer op amp (LPV811/OPA333) and ESD clamp diodes remain uncommitted pending common-mode headroom, leakage current, and bench validation.
2. **CR2032 Loaded Voltage Sag:** Pulse load sag must be measured across battery discharge state to confirm VDD stays safely above 1.7 V brownout threshold.
3. **Mechanical Enclosure Fit:** Enclosure outline and wrist contact snap locations to be finalized with SolidWorks model.
