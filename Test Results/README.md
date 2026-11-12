# Stage 1 Verification & Test Results

This directory consolidates the formal verification logs, test matrices, and simulation test results across all Stage 1 engineering disciplines.

---

## 1. Summary of Stage 1 Test Disciplines

| Test Discipline | Tool / Environment | Test Focus | Status | Deliverables & Reports |
| :--- | :--- | :--- | :--- | :--- |
| **Numerical DC & Transient** | MATLAB R2024b | Voltage divider equations, 4-scenario RC settling, late-window averaging | **PASS** | [`MATLAB Model/README.md`](../MATLAB%20Model/README.md), CSV logs, calculation PDF |
| **SPICE Pulse Simulation** | NI Multisim 14.3 | Pulse generator timing, node probe voltages, transient edge decay | **PASS** | [`Digital Circuit Data/README.md`](../Digital%20Circuit%20Data/README.md), scope captures |
| **Firmware Status Logic** | Wokwi (ESP32-C3) | Resistance estimation formula, boundary checks, LED driver logic | **PASS** | [`Wokwi_Initial_Potentiometer_Check.md`](Wokwi_Initial_Potentiometer_Check.md), test chart |
| **PCB Electrical Rules** | KiCad 10 (`kicad-cli`) | Pin types, power inputs, floating nodes, ERC checks | **PASS (0 Errors)** | [`PCB Design/erc_report.rpt`](../PCB%20Design/erc_report.rpt) |
| **PCB Physical Design Rules** | KiCad 10 (`kicad-cli`) | Trace clearances, shorts, courtyards, solder mask bridges | **PASS (0 Errors)** | [`PCB Design/drc_report.rpt`](../PCB%20Design/drc_report.rpt) |
| **Mechanical Fit & Mating** | SolidWorks 2026 | Enclosure cavity, PCB mounting shelf, strap lugs, battery bay | **PASS** | [`SolidWorks Design/README.md`](../SolidWorks%20Design/README.md), STEP/STL models |

---

## 2. Detailed Test Logs

- [Wokwi Potentiometer Sweep & Threshold Test Log](Wokwi_Initial_Potentiometer_Check.md)
- [MATLAB Status & Waveform Numerical Tables](../MATLAB%20Model/README.md)
- [Multisim Oscilloscope Probe Data Points](../Digital%20Circuit%20Data/README.md)
- [KiCad 10 ERC and DRC Verification Reports](../PCB%20Design/README.md)
