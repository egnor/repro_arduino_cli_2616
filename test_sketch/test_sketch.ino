#include <Arduino.h>

void setup() {
  Serial.begin(9600);
  Serial.println("Hello, world!");
}

void loop() {
  Serial.println("Looping...");
  delay(500);
}
