// ESD wristband status-logic simulation for a Wokwi ESP32-C3 board.
// This is a proxy for the nRF52840 firmware, not a hardware-equivalent test.
// The potentiometer feeds a test voltage directly to the ADC; it does not
// simulate the wristband's RC network or generate the measured pulse waveform.

const uint8_t SENSE_PIN = 0;      // ESP32-C3 GPIO0 / ADC input; connect pot SIG here.
const uint8_t GREEN_LED_PIN = 4;  // GPIO4 -> 220 ohm resistor -> green LED anode.
const uint8_t YELLOW_LED_PIN = 5; // GPIO5 -> 220 ohm resistor -> yellow LED anode.
const uint8_t RED_LED_PIN = 6;    // GPIO6 -> 220 ohm resistor -> red LED anode.

const float VREF_VOLTS = 3.0f;                 // Model the CR2032 nominal nRF VDD.
const float SERIES_RESISTOR_OHMS = 1000000.0f; // Rlimit in the circuit model.
const float RETURN_RESISTOR_OHMS = 1000000.0f; // Rground in the circuit model.
const float OPEN_CIRCUIT_VOLTS = 0.02f;        // Treat readings at/below this as open/invalid.
const float MAX_MODEL_SENSE_VOLTS = VREF_VOLTS * RETURN_RESISTOR_OHMS /
                                    (SERIES_RESISTOR_OHMS + RETURN_RESISTOR_OHMS);

const float GOOD_HIGH_OHMS = 5000000.0f;
const float WARNING_LOW_OHMS = 5000000.0f;
const float WARNING_HIGH_OHMS = 35000000.0f;

const uint8_t ADC_SAMPLES = 8;
const uint16_t SAMPLE_INTERVAL_MS = 250;

enum Status : uint8_t {
  STATUS_GOOD,
  STATUS_WARNING,
  STATUS_FAIL
};

float readSenseVoltage() {
  uint32_t totalMillivolts = 0;

  // Average a few readings to make the potentiometer test less jumpy.
  for (uint8_t sample = 0; sample < ADC_SAMPLES; sample++) {
    totalMillivolts += analogReadMilliVolts(SENSE_PIN);
    delay(2);
  }

  return (totalMillivolts / static_cast<float>(ADC_SAMPLES)) / 1000.0f;
}

float estimateSkinResistance(float senseVoltage) {
  // Divider equation for the project's settled measurement:
  // Vsense = Vref * Rreturn / (Rlimit + Rskin + Rreturn)
  // Rearranged to estimate Rskin from the test voltage.
  if (senseVoltage <= OPEN_CIRCUIT_VOLTS || senseVoltage >= VREF_VOLTS) {
    return -1.0f; // Open/near-zero or invalid ADC reading.
  }
  if (senseVoltage > MAX_MODEL_SENSE_VOLTS) {
    return -2.0f; // Above the divider's maximum possible sense voltage.
  }

  const float resistance = (VREF_VOLTS * RETURN_RESISTOR_OHMS / senseVoltage)
                           - SERIES_RESISTOR_OHMS - RETURN_RESISTOR_OHMS;
  return resistance;
}

Status classifyResistance(float resistanceOhms) {
  if (resistanceOhms < 0.0f) {
    return STATUS_FAIL;
  }

  if (resistanceOhms < GOOD_HIGH_OHMS) {
    return STATUS_GOOD;
  }

  if (resistanceOhms >= WARNING_LOW_OHMS && resistanceOhms <= WARNING_HIGH_OHMS) {
    return STATUS_WARNING;
  }

  // Values above 35 MOhm fail; open/invalid readings were handled above.
  return STATUS_FAIL;
}

void showStatus(Status status) {
  // Turn off all indicators first so only one status LED is on.
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(YELLOW_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);

  if (status == STATUS_GOOD) {
    digitalWrite(GREEN_LED_PIN, HIGH);
  } else if (status == STATUS_WARNING) {
    digitalWrite(YELLOW_LED_PIN, HIGH);
  } else {
    digitalWrite(RED_LED_PIN, HIGH);
  }
}

void printReading(float voltage, float resistanceOhms, Status status) {
  Serial.print("ADC voltage: ");
  Serial.print(voltage, 3);
  Serial.print(" V | Estimated resistance: ");

  if (resistanceOhms < 0.0f) {
    if (resistanceOhms <= -2.0f) {
      Serial.print("OUT OF MODEL RANGE");
    } else {
      Serial.print("OPEN/INVALID");
    }
  } else {
    Serial.print(resistanceOhms / 1000000.0f, 3);
    Serial.print(" MOhm");
  }

  Serial.print(" | Status: ");
  if (status == STATUS_GOOD) {
    Serial.println("GOOD");
  } else if (status == STATUS_WARNING) {
    Serial.println("WARNING");
  } else {
    Serial.println("FAIL");
  }
}

void setup() {
  pinMode(SENSE_PIN, INPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);

  analogReadResolution(12); // ESP32-C3 ADC range is represented as 0-4095 here.
  Serial.begin(115200);
  delay(200);
  Serial.println("ESD wristband threshold simulation (ESP32-C3 proxy)");
  Serial.println("Adjust the potentiometer and compare its voltage to the README table.");
}

void loop() {
  const float voltage = readSenseVoltage();
  const float resistanceOhms = estimateSkinResistance(voltage);
  const Status status = classifyResistance(resistanceOhms);

  showStatus(status);
  printReading(voltage, resistanceOhms, status);
  delay(SAMPLE_INTERVAL_MS);
}
