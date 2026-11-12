// ESD Wristband Monitoring Firmware
// Bench/prototype topology: pulse -> 1 MOhm limit -> skin path -> ADC node -> 1 MOhm pull-down -> ground.

// Logical pin assignments; confirm these aliases against the selected nRF52840 board.
const int ADC_PIN = A0;
const int PULSE_PIN = 7;
const int GREEN_LED_PIN = 8;
const int YELLOW_LED_PIN = 9;
const int RED_LED_PIN = 10;

const float PULSE_HIGH_VOLTS = 3.0f; // Nominal CR2032-powered pulse; verify loaded VDD.
const float ADC_FULL_SCALE_VOLTS = 3.6f; // Assumes SAADC VREF=0.6 V and gain=1/6; verify target configuration.
const float ADC_MAX_COUNTS = 4095.0f;
const float SERIES_RESISTOR_OHMS = 1000000.0f;
const float PULLDOWN_RESISTOR_OHMS = 1000000.0f;
const float MAX_MODEL_SENSE_VOLTS = PULSE_HIGH_VOLTS * PULLDOWN_RESISTOR_OHMS /
                                    (SERIES_RESISTOR_OHMS + PULLDOWN_RESISTOR_OHMS);

const float GOOD_HIGH_OHMS = 5000000.0f; // 5 MΩ (Good below this)
const float WARN_LOW_OHMS = 5000000.0f;   // 5 MΩ
const float WARN_HIGH_OHMS = 35000000.0f; // 35 MΩ
const int WAVEFORM_SAMPLE_COUNT = 300;
const int LATE_SAMPLE_START = 250;
const int SAMPLE_INTERVAL_US = 250;

enum ESDStatus {
  STATUS_GOOD,
  STATUS_WARNING,
  STATUS_FAIL
};

float readVoltage() {
  int raw = analogRead(ADC_PIN);
  return (raw * ADC_FULL_SCALE_VOLTS) / ADC_MAX_COUNTS;
}

float estimateResistanceFromVoltage(float voltage) {
  // Vadc = Vdrive * Rpull / (Rseries + Rskin + Rpull)
  // Solve for Rskin using the measured voltage during the high pulse.
  if (voltage <= 0.02f) {
    return -1.0f;
  }
  if (voltage > MAX_MODEL_SENSE_VOLTS) {
    return -2.0f;
  }

  float resistance = (PULSE_HIGH_VOLTS * PULLDOWN_RESISTOR_OHMS / voltage)
                     - SERIES_RESISTOR_OHMS - PULLDOWN_RESISTOR_OHMS;
  return resistance;
}

ESDStatus classifyResistance(float resistanceOhms) {
  if (resistanceOhms < 0.0f) {
    return STATUS_FAIL;
  }

  if (resistanceOhms < GOOD_HIGH_OHMS) {
    return STATUS_GOOD;
  }

  if (resistanceOhms >= WARN_LOW_OHMS && resistanceOhms <= WARN_HIGH_OHMS) {
    return STATUS_WARNING;
  }

  // Values above 35 MOhm and outside the defined ranges fail.
  return STATUS_FAIL;
}

void setStatusLED(ESDStatus status) {
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(YELLOW_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);

  switch (status) {
    case STATUS_GOOD:
      digitalWrite(GREEN_LED_PIN, HIGH);
      break;

    case STATUS_WARNING:
      digitalWrite(YELLOW_LED_PIN, HIGH);
      break;

    case STATUS_FAIL:
      digitalWrite(RED_LED_PIN, HIGH);
      break;
  }
}

void printStatus(float resistanceOhms, float earlyVoltage, float plateauVoltage,
                 long settlingTimeUs, ESDStatus status) {
  float edgeDrop = earlyVoltage - plateauVoltage;
  if (edgeDrop < 0.0f) {
    edgeDrop = -edgeDrop;
  }
  Serial.print("Resistance: ");
  if (resistanceOhms <= -2.0f) {
    Serial.print("OUT OF MODEL RANGE");
  } else if (resistanceOhms < 0.0f) {
    Serial.print("OPEN/INVALID");
  } else {
    Serial.print(resistanceOhms);
    Serial.print(" ohms");
  }
  Serial.print(" | Early: ");
  Serial.print(earlyVoltage, 3);
  Serial.print(" V | Plateau: ");
  Serial.print(plateauVoltage, 3);
  Serial.print(" V | Edge drop: ");
  Serial.print(edgeDrop, 3);
  Serial.print(" V | Settling: ");
  if (settlingTimeUs >= 0) {
    Serial.print(settlingTimeUs);
    Serial.print(" us | ");
  } else {
    Serial.print("n/a | ");
  }

  if (status == STATUS_GOOD) {
    Serial.println("GOOD");
  } else if (status == STATUS_WARNING) {
    Serial.println("WARNING");
  } else {
    Serial.println("FAIL");
  }
}

void setup() {
  pinMode(ADC_PIN, INPUT);
  pinMode(PULSE_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);

  Serial.begin(115200);
  analogReadResolution(12);
  // This sets conversion resolution only. Configure the bare-SoC SAADC reference,
  // gain, and acquisition time in the selected Nordic SDK/board layer; the voltage
  // conversion above assumes 0.6 V internal reference and 1/6 gain (3.6 V full scale).
  delay(500);

  Serial.println("ESD wristband monitor started");
}

void loop() {
  float earlyVoltage;
  float plateauVoltage = 0.0f;
  float sampleVoltages[WAVEFORM_SAMPLE_COUNT];
  unsigned long sampleTimesUs[WAVEFORM_SAMPLE_COUNT];
  long settlingTimeUs = -1;

  digitalWrite(PULSE_PIN, HIGH);
  unsigned long pulseStartUs = micros();
  delayMicroseconds(25);
  earlyVoltage = readVoltage();

  for (int sample = 0; sample < WAVEFORM_SAMPLE_COUNT; sample++) {
    unsigned long targetTimeUs = pulseStartUs +
        (unsigned long)(sample + 1) * SAMPLE_INTERVAL_US;
    while ((long)(micros() - targetTimeUs) < 0) {
    }
    sampleVoltages[sample] = readVoltage();
    sampleTimesUs[sample] = micros() - pulseStartUs;
    if (sample >= LATE_SAMPLE_START) {
      plateauVoltage += sampleVoltages[sample];
    }
  }
  digitalWrite(PULSE_PIN, LOW);
  plateauVoltage /= (WAVEFORM_SAMPLE_COUNT - LATE_SAMPLE_START);

  float edgeMagnitude = earlyVoltage - plateauVoltage;
  if (edgeMagnitude < 0.0f) {
    edgeMagnitude = -edgeMagnitude;
  }
  float settleTolerance = edgeMagnitude * 0.05f;
  float adcNoiseFloor = 2.0f * ADC_FULL_SCALE_VOLTS / ADC_MAX_COUNTS;
  if (edgeMagnitude > adcNoiseFloor) {
    for (int sample = 0; sample < WAVEFORM_SAMPLE_COUNT; sample++) {
      float errorFromPlateau = sampleVoltages[sample] - plateauVoltage;
      if (errorFromPlateau < 0.0f) {
        errorFromPlateau = -errorFromPlateau;
      }
      if (errorFromPlateau <= settleTolerance) {
        settlingTimeUs = (long)sampleTimesUs[sample];
        break;
      }
    }
  }

  // Keep LEDs based on the settled plateau; log edge drop for later calibration.
  float resistanceOhms = estimateResistanceFromVoltage(plateauVoltage);
  ESDStatus status = classifyResistance(resistanceOhms);

  setStatusLED(status);
  printStatus(resistanceOhms, earlyVoltage, plateauVoltage, settlingTimeUs, status);

  delay(1000);
}
