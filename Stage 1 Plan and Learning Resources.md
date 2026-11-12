# Stage 1 Completion Summary, Deliverables & Learning Resources

## Stage 1 status

All Stage 1 engineering disciplines are complete: MATLAB numerical modeling, Multisim SPICE simulation, Arduino prototype firmware, Wokwi proxy simulation, KiCad 10 physical PCB layout, and SolidWorks 3D mechanical enclosure design.

| Workstream | Status | Stage 1 evidence |
| --- | --- | --- |
| MATLAB analysis | Complete | Model, plots, calculation report, and CSV outputs in `MATLAB Model` |
| Multisim simulation | Complete | Native `.ms14` design and pulse/scope analysis in `Digital Circuit Data` |
| Arduino firmware | Complete for current prototype logic | Bare nRF52840 SoC target logic and status/waveform behavior in `Arduino Code` |
| Wokwi simulation | Complete for Stage 1 proxy testing | ESP32-C3 logic test and potentiometer status checks in `Wokwi`; not nRF52840 hardware validation |
| KiCad PCB design | Complete | Schematic, selected footprints, routed board, ERC/DRC, reviewed fabrication outputs |
| SolidWorks mechanical design | Complete | Wristband, contacts, housing, cable route, board fit, and assembly views |

## Design facts to carry forward

- The real MCU/PCB target is the bare Nordic nRF52840 SoC. The ESP32-C3 Wokwi simulation is only a proxy for shared status logic.
- Power plan: CR2032 primary cell, nominal 3.0 V. Validate loaded SoC supply, radio/LED peak-current droop, and measured runtime before release. Never charge the CR2032; USB can be programming/external power only.
- Intended indication/power behavior: one selected status LED blinks for an initial 200 ms visibility target, then turns off while the MCU sleeps for most of the roughly 1.25 s cycle. Verify actual LED visibility and SoC sleep current in the hardware stage.
- Buzzer: Phase 2 optional feature; exclude it from the Phase 1 PCB and evaluate only after prototype CR2032 peak-current/runtime measurements.
- Current status bands: Good below 5 MOhm for a connected path; Warning from 5 through 35 MOhm inclusive; Fail above 35 MOhm or open circuit.
- The current parallel-RC values are sensitivity-study inputs, not calibrated values for skin, fit, or moisture.
- Stage 1 is design readiness. Do not order or fabricate the PCB until the KiCad/Mechanical review gate is complete.

## Notes: Stage 1 software issues

- **Multisim SPICE import:** Multisim 14.3 reported a missing `SPICEWEB.TPL` when opening the `.cir` netlist. The native `.ms14` schematic is the working design record; use the documented manual-schematic workflow unless NI repairs the importer/template.
- **MATLAB launch error:** A stray leading `x` before the first comment caused “Unrecognized function or variable 'x'.” Removing it restored script execution. MATLAB subsequently ran the model and exported the calculation CSVs.
- **Wokwi input interpretation:** Wokwi has no separate pin labeled “ADC”; the ESP32-C3's GPIO0 is used as the ADC input. The potentiometer directly sets a test voltage, not wrist resistance or an RC waveform. Inputs above the modeled 1.5 V sense maximum are out-of-model and must not map to 0 Ohm/Good.
- **Pulse-profile mismatch:** The manual Multisim screenshot used 0.5 ms high / 1 ms period. The 75 ms profile is for waveform characterization; the proposed 250 ms classification window is separate. Label results with their profile and do not compare them as equivalent tests.
- **RC settling:** For the ideal 40 MOhm / 10 nF case, 57 ms is 5% of the initial transient amplitude, not 5% of the final 0.07143 V plateau. Settling to within 5% of that final value is about 114.12 ms. MATLAB records the resulting 75 ms late-window bias; use a later classification window and confirm SAADC acquisition behavior.
- **ADC and power implementation:** `analogReadResolution(12)` alone does not configure the bare nRF52840 SAADC reference, gain, or acquisition time. The current `.ino` uses busy-wait sampling and `delay()` and leaves its selected LED on; the intended 200 ms blink and majority-sleep behavior still needs Nordic-SDK implementation and measured current validation.
- **Battery limitation:** The CR2032 is primary and cannot be charged over USB. Its nominal 3.0 V matches the model assumption, but loaded voltage sag and peak-current margin remain unverified for the nRF radio, pulse, and LED loads.

## Stage 1 Completed Deliverables Checklist

### KiCad PCB Design [COMPLETED]
- [x] Single authoritative KiCad 10 project established (ESD_Wristband_Monitor.kicad_pro, .kicad_sch, .kicad_pcb).
- [x] Exact Nordic nRF52840-QIAA aQFN-73 package selected with reference clocks (32 MHz HFXO, 32.768 kHz LFXO), decoupling, and RF match network.
- [x] Pulse/sense measurement path captured ({limit} = 1	ext{ M}\Omega$, {ground} = 1	ext{ M}\Omega$, 3mm gold contact pads J1, J2, and earth ground snap J3).
- [x] 2-layer routed board (.0 	imes 40.0	ext{ mm}$), Keystone 3002 CR2032 retainer clip, SWD header, and test points.
- [x] Passed Electrical Rules Check (erc_report.rpt: 0 Errors, 0 Warnings).
- [x] Passed Design Rules Check (drc_report.rpt: 0 Violations, 0 Unconnected Nets).
- [x] 3D STEP solid model (ESD_Wristband_Monitor.step) exported for mechanical integration.
- [x] Fabrication outputs (Gerbers/drill) held unreleased until Stage 2 gate review.

### SolidWorks Mechanical Design [COMPLETED]
- [x] Defined wristband parameters: .0	ext{ mm}$ quick-release strap lugs supporting adult wrist circumferences 	ext{–}210	ext{ mm}$.
- [x] Internal electronics cavity modeled (.0 	imes 41.0 	imes 9.6	ext{ mm}$), providing .5	ext{ mm}$ lateral clearance around the PCB.
- [x] 4 internal mounting standoffs ( = -1.6	ext{ mm}$) and corner M2 screw bosses modeled.
- [x] 3 optical light-pipe apertures ($arnothing 2.0	ext{ mm}$) aligned over Good, Warning, and Fail status LEDs.
- [x] Twist-lock coin-slot battery door modeled for toolless CR2032 coin cell replacement.
- [x] Imported KiCad 3D STEP model (ESD_Wristband_Monitor_PCB.step) into master assembly to verify zero collision and proper standoff mating.
- [x] Exported high-resolution CAD isometric renders (enclosure_cad_render.png) and exploded assembly views (enclosure_exploded_view.png).

## KiCad learning resources

- [Official KiCad documentation](https://docs.kicad.org/) includes the schematic editor, PCB editor, and Gerber viewer guides.
- [Getting Started in KiCad](https://docs.kicad.org/10.0/en/getting_started_in_kicad/getting_started_in_kicad.html) is the recommended schematic-to-PCB introduction.
- [KiCad beginner video search: schematic, footprints, routing, ERC/DRC](https://www.youtube.com/results?search_query=KiCad+beginner+schematic+footprints+routing+ERC+DRC+tutorial)

## SolidWorks learning resources

- [SOLIDWORKS Training](https://www.solidworks.com/support/training) provides official training information and files.
- [SOLIDWORKS Design Essentials](https://www.solidworks.com/support/training/solidworks-essentials) is the structured beginner course.
- [SolidWorks beginner video search: sketches, features, parts, assemblies](https://www.youtube.com/results?search_query=SOLIDWORKS+beginner+sketch+extrude+fillet+part+assembly+tutorial)

## Stage 1 exit checklist

- [x] MATLAB, Multisim, Arduino firmware, and Wokwi Stage 1 work completed and organized.
- [x] Exact nRF52840 SoC package variant (nRF52840-QIAA aQFN-73) and footprint selected and documented.
- [x] KiCad schematic passes ERC (0 errors); PCB passes DRC (0 shorts, 0 clearance errors) and fabrication outputs reviewed and held unreleased.
- [x] SolidWorks wristband/enclosure assembly fits the approved PCB outline (32 × 40 mm) with snap contact ports, 20 mm strap lugs, mounting bosses, and battery access door.
- [x] KiCad board and SolidWorks CAD models reviewed together before Stage 2 physical prototyping.

## Stage 2 preview

After the joint design review, order the approved components, fabricate/assemble the PCB, and compare bench measurements with MATLAB/Multisim predictions. Treat fit and moisture classification as later research questions requiring controlled tests.
