#include <Arduino_HS300x.h>   // Temp & humidity sensor library

// Pin definitions
const int LDR_PIN = A0;       // Photoresistor output
const int GAS_PIN = A1;       // Op-amp amplified MQ-2 output

void setup() {
  Serial.begin(115200);
  while (!Serial);            // Wait for Serial Monitor (USB)

  Serial1.begin(9600);        // UART to second Arduino (TX = D1, RX = D0)

  Serial.println("=== SENSOR NODE STARTED (LDR + GAS + TEMP + HUM) ===");

  // Initialise HS3003 sensor
  if (!HS300x.begin()) {
    Serial.println("HS3003 init failed!");
    while (1) {
      delay(1000);
    }
  }
  Serial.println("HS3003 initialised OK");
}

void loop() {

  // ---------- LDR (Light) ----------
  int   ldrRaw      = analogRead(LDR_PIN);              // 0–1023
  float ldrVoltage  = ldrRaw * (3.3 / 1023.0);
  float brightness  = (ldrVoltage / 3.3) * 100.0;

  // ---------- MQ-2 Gas ----------
  int   gasRaw      = analogRead(GAS_PIN);              // 0–1023
  float gasVoltage  = gasRaw * (3.3 / 1023.0);
  float gasLevel    = (gasVoltage / 3.3) * 100.0;

  // ---------- Temp & Humidity ----------
  float temperature = HS300x.readTemperature();         // °C
  float humidity    = HS300x.readHumidity();            // %RH

  // ---------- Serial Monitor Output ----------
  Serial.println("---- SENSOR READINGS ----");

  Serial.print("LDR   raw: ");
  Serial.print(ldrRaw);
  Serial.print("  |  V: ");
  Serial.print(ldrVoltage, 3);
  Serial.print(" V  |  Brightness: ");
  Serial.print(brightness, 1);
  Serial.println(" %");

  Serial.print("GAS  raw: ");
  Serial.print(gasRaw);
  Serial.print("  |  V: ");
  Serial.print(gasVoltage, 3);
  Serial.print(" V  |  Gas Level: ");
  Serial.print(gasLevel, 1);
  Serial.println(" %");

  Serial.print("TEMP: ");
  Serial.print(temperature, 2);
  Serial.print(" °C   |   HUM: ");
  Serial.print(humidity, 2);
  Serial.println(" %RH");

  Serial.println();   // blank line for readability


  // ---------- UART Transmission to second Arduino ----------
  // CSV: BRIGHTNESS,GASLEVEL,TEMP,HUMID
  Serial1.print(brightness, 1);
  Serial1.print(",");
  Serial1.print(gasLevel, 1);
  Serial1.print(",");
  Serial1.print(temperature, 2);
  Serial1.print(",");
  Serial1.print(humidity, 2);
  Serial1.println();

  delay(500);
}
