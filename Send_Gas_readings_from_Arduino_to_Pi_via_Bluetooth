#include <Wire.h>

int mq2_value = 0;

void setup() {
  Wire.begin(8); // Set as I²C slave with address 0x08
  Wire.onRequest(requestEvent); // What to do when Pi asks
  Serial.begin(9600);
}

void loop() {
  mq2_value = analogRead(A0);  // fast, non-blocking
  delay(200);
}

void requestEvent() {
  Wire.write((mq2_value >> 8) & 0xFF); // send high byte
  Wire.write(mq2_value & 0xFF);        // send low byte
}
