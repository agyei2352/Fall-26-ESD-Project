# Initial Wokwi Potentiometer Check

- **Date:** November 9, 2026
- **Test type:** Wokwi firmware/status-logic simulation
- **Input:** Potentiometer connected to the ESP32-C3 proxy ADC input
- **Procedure:** Adjust the potentiometer to seven input voltages and compare the reported estimated resistance/status and indicator LED.
- **Scope note:** The potentiometer directly supplies a voltage. This is not a measurement of a wrist, skin impedance, fit, or moisture.
- **Supply-model note:** These original screenshots used the previous 3.3 V interpretation. They are historical; retest using the 3.0 V nominal CR2032 model targets below. Wokwi does not model the CR2032's source impedance or loaded voltage sag.

| Test point | ADC voltage | Estimated resistance | Status observed with previous sketch | Status expected with revised table | Retest |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 1.275 V | 0.588 MOhm | Good / green | Good / green | Confirm |
| 2 | 0.440 V | 5.500 MOhm | Warning / yellow | Warning / yellow | Confirm |
| 3 | 0.107 V | 28.841 MOhm | Fail / red | Warning / yellow | Required |
| 4 | 1.081 V | 1.053 MOhm | Fail / red | Good / green | Required |
| 5 | 0.462 V | 5.143 MOhm | Warning / yellow | Warning / yellow | Confirm |
| 6 | 0.276 V | 9.957 MOhm | Warning / yellow | Warning / yellow | Confirm |
| 7 | 0.138 V | 21.913 MOhm | Fail / red | Warning / yellow | Required |
| Pot at upper end | 2.727 V | Not physically representable by the modeled divider | Old sketch incorrectly showed 0.000 MOhm / Good | Out of model range / Fail | Required |

## Conclusion

The seven statuses above were captured with the previous threshold version. Under the revised table, Good is below 5 MOhm for a connected path, Warning is 5-35 MOhm inclusive, and Fail is above 35 MOhm or open. The three rows marked Required need retesting under the revised sketch.

## Revised-threshold rerun

| ADC voltage | Estimated resistance | Serial status | Observed LED | Result |
| ---: | ---: | --- | --- | --- |
| 0.834 V | 1.957 MOhm | Good | Green | Pass |
| Not visible in screenshot | Not visible | Not visible | Yellow | Visual-only; capture Serial Monitor value |
| Not visible in screenshot | Not visible | Not visible | Red | Visual-only; capture Serial Monitor value |

The 1.957 MOhm result is Good under the revised <5 MOhm rule. The yellow/red screenshots show the corresponding indicators, but their numeric readings are not visible, so they do not yet verify the resistance thresholds. Next, retest the changed historical cases (1.053 MOhm, 21.913 MOhm, 28.841 MOhm), plus exact 5 MOhm, 35 MOhm, and a value above 35 MOhm, recording the Serial Monitor each time.

## CR2032 nominal retest targets

For `Rlimit = Rground = 1 MOhm` and `Vdrive = 3.0 V`, use these potentiometer sense targets:

| Skin-path resistance | Target sense voltage | Expected status |
| ---: | ---: | --- |
| 500 kOhm | 1.200 V | Good |
| 1 MOhm | 1.000 V | Good |
| 2 MOhm | 0.750 V | Good |
| 5 MOhm | 0.429 V | Warning |
| 10 MOhm | 0.250 V | Warning |
| 20 MOhm | 0.136 V | Warning |
| 35 MOhm | 0.081 V | Warning |
| 40 MOhm | 0.071 V | Fail |
| Open | 0 V | Fail |
