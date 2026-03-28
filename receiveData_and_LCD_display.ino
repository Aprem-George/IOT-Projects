#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Change address 0x27 to 0x3F if your LCD uses that address
LiquidCrystal_I2C lcd(0x27, 16, 2);

String incomingData = "";

// Helper to split CSV fields
String getValue(String data, char separator, int index) {
  int found = 0;
  int start = 0;

  for (int i = 0; i < data.length(); i++) {
    if (data.charAt(i) == separator || i == data.length() - 1) {
      if (found == index) {
        int end = (i == data.length() - 1) ? i + 1 : i;
        return data.substring(start, end);
      }
      found++;
      start = i + 1;
    }
  }
  return "";
}

void setup() {
  // USB serial for debugging
  Serial.begin(115200);
  while (!Serial);

  // UART from Nano (Sensor Node)
  // On MKR1010, Serial1 uses:
  // RX1 = pin 13, TX1 = pin 14
  Serial1.begin(9600);

  // Init LCD
  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("Receiver Node");
  lcd.setCursor(0, 1);
  lcd.print("Waiting data...");
  delay(1500);
  lcd.clear();

  Serial.println("=== MKR1010 Receiver Ready ===");
}

void loop() {
  // Read characters from Serial1 until newline
  while (Serial1.available()) {
    char c = Serial1.read();

    if (c == '\n') {
      if (incomingData.length() > 0) {
        processData(incomingData);
      }
      incomingData = "";
    } else if (c != '\r') {
      incomingData += c;
    }
  }
}

void processData(String data) {
  Serial.print("Raw received: ");
  Serial.println(data);

  // Parse CSV: brightness, gasLevel, temperature, humidity
  float brightness  = getValue(data, ',', 0).toFloat();
  float gasLevel    = getValue(data, ',', 1).toFloat();
  float temperature = getValue(data, ',', 2).toFloat();
  float humidity    = getValue(data, ',', 3).toFloat();

  // Debug to Serial
  Serial.print("Brightness: ");
  Serial.print(brightness, 1);
  Serial.print("%  |  Gas: ");
  Serial.print(gasLevel, 1);
  Serial.print("%  |  Temp: ");
  Serial.print(temperature, 2);
  Serial.print("C  |  Hum: ");
  Serial.print(humidity, 1);
  Serial.println("%RH");

  // === Update LCD ===
  lcd.clear();

  // Line 1: Light & Gas
  lcd.setCursor(0, 0);
  lcd.print("L:");
  lcd.print(brightness, 0);
  lcd.print("% ");

  lcd.print("G:");
  lcd.print(gasLevel, 0);
  lcd.print("%");

  // Line 2: Temp & Humidity
  lcd.setCursor(0, 1);
  lcd.print("T:");
  lcd.print(temperature, 1);
  lcd.print("C ");

  lcd.print("H:");
  lcd.print(humidity, 0);
  lcd.print("%");
}
