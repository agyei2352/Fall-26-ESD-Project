# SAADC Interface Review

## Current decision

- Retain the 1 MOhm wristband series resistor and the 1 MOhm return resistor.
- Develop a **protected buffer between the Nylon B/sense node and the nRF52840 SAADC** as the preferred candidate. This is an analysis direction only; do not select an op amp, alter thresholds, or route the PCB until the exact nRF52840 product-specification revision and CR2032 cell datasheet are reviewed.
- Do not approve the LPV811 as-is. The supplied Flux review reports that its common-mode range lacks headroom at the low supply case; confirm against the exact component datasheet and actual SoC rail before considering alternatives.
- Do not lower Rground to 470 kOhm as a drop-in fix: although that improves provisional source-impedance targets, it changes the divider transfer function and requires recalculating all voltage thresholds and protection behavior.

## Divider source impedance

For the present passive network:

```text
Rsource_at_ADC = Rground || (Rskin + Rlimit)
```

Using Rground = Rlimit = 1 MOhm gives nominal source impedance around:

| Rskin | Rsource at ADC |
| ---: | ---: |
| 5 MOhm | 0.857 MOhm |
| 35 MOhm | 0.973 MOhm |
| 40 MOhm | 0.976 MOhm |
| Open | 1.000 MOhm |

These are ideal calculations. Resistor tolerance, protection leakage, PCB contamination, contact leakage, and SAADC sampling-capacitor behavior can change the result. The Flux review cites 800 kOhm as a **provisional** source-resistance recommendation at 40 us acquisition; verify the exact recommendation and SAADC configuration from the uploaded Nordic nRF52840 Product Specification v1.11 before relying on it.

## RC settling and measurement timing

For Rskin = 40 MOhm and Cskin = 10 nF, the model gives:

- External RC time constant: about 19.05 ms.
- Settling to within 5% of the final plateau: about 114.12 ms. This is stricter than 5% of the initial transient amplitude.
- True settled sense voltage at Vdrive = 3.0 V: about 0.07143 V, corresponding to 40 MOhm in the ideal divider.
- The earlier 75 ms late-window calculation (62.75-75 ms) averaged about 0.11054 V, inferring about 25.14 MOhm / Warning instead of the expected Fail; retain this as historical characterization data, not a valid classification result.

Adopt the following distinct profiles:

- **75 ms characterization:** retain for waveform plots and edge/settling analysis; do not use its current late-window average as a qualified resistance classification for the slowest RC case.
- **250 ms classification measurement:** proposed for status decisions. The guarded 50-sample window triggers at 237.50-249.75 ms (250 us apart). With provisional 40 us acquisition, the final capture completes at 249.79 ms, 0.21 ms before pulse fall. MATLAB's ideal 40 MOhm / 10 nF mean is 0.071433 V, inferring 39.998 MOhm / Fail. Verify the exact SAADC acquisition and pulse-driver timing; if either exceeds this margin, move the window earlier or extend/recalculate the pulse and cycle.
- After the 250 ms classification measurement, blink only the selected status LED for an initial 200 ms visibility target, turn all LEDs off, and put the MCU into timer-wake low-power sleep for about 800 ms in a roughly 1.25 s cycle. A buzzer is reserved for Phase 2 and is excluded from the Phase 1 CR2032 load. The current `.ino` is not that implementation; it busy-waits, uses `delay()`, and holds a status LED on.

For each classification window, MATLAB and Multisim should report the discrete average sense voltage actually used by firmware, the resistance inferred from that average, the final settled value, and the status discrepancy (if any). Distinguish 5% transient decay from settling to within 5% of the final voltage. Do not label a result “plateau” unless it passes the final-voltage settling criterion.

## Buffer candidate requirements

Any proposed buffer/protection stage must be analyzed at the ADC sense node and must:

- Preserve the existing Rlimit and Rground topology and nominal status thresholds unless a separately reviewed recalculation is approved.
- Have input common-mode range covering the full sense-voltage envelope at minimum and maximum CR2032-loaded VDD.
- Have low, specified input bias/leakage and protection leakage so the 1 MOhm/40 MOhm network is not materially loaded.
- Settle to the required error within the defined acquisition/measurement window and drive the SAADC sampling capacitor/source impedance.
- Meet coin-cell sleep/active current needs and have defined behavior during startup, brownout, open circuit, ESD/fault events, and debugger/USB connection.
- Be evaluated from exact component datasheets and measurements; the generic buffer recommendation is not yet a qualified schematic decision.

## Blocking inputs

1. Upload the exact Nordic nRF52840 Product Specification v1.11 PDF (and identify package variant) so SAADC reference, gain, source impedance/acquisition guidance, input limits, and pin mapping can be checked.
2. Select the CR2032 manufacturer/part and provide its discharge/impedance data for the required current pulses and temperature range.
3. Decide/verify the actual pulse-driver implementation, SAADC SDK configuration, LED blink duration, and timer-sleep API for the bare SoC.
4. Review the selected buffer's datasheet and protection network before schematic approval.
