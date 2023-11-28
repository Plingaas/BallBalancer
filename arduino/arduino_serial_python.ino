#include "PlatformController.hpp"

Platform platform;
void setup() {
  Serial.begin(230400);
  Serial.setTimeout(0);

  
  delay(1000); // Stabilze setup

  // Calibrate
  platform.attachSwitches(26, 25, 27);
  platform.calibrate();

  platform.setAcceleration(500);
  platform.setMaxSpeed(1000);
  platform.setAngles(32, 28, 29.6); // Go to zeroposition.

  platform.setAcceleration(150000); // Causes jittering, but must be high enoug
  platform.setMaxSpeed(50000);
}

byte data[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

unsigned long prevTime = micros();
unsigned long lastrx = micros();
unsigned long rate = 3e3; // Every 30ms. python should be 30fps -> 33ms
unsigned long now = 0;
unsigned long dt = 0;

void loop() {
  now = micros();
  dt = now - prevTime;
  prevTime = now;
  platform.update(dt);

  // Serial communication
  if (now - lastrx >= rate) {
    lastrx += rate;
    bool recv = false;
    while (Serial.available() >= 6) {
      Serial.readBytes(data, 6);
      recv = true;
    }

    if (recv) {
      float angle1 = (float)data[0] + ((float)data[1])/256.0; // First byte is angle integer value, second byte is decimal value given as an integer (0-255), so we downscale to 0-0.9999
      float angle2 = (float)data[2] + ((float)data[3])/256.0;
      float angle3 = (float)data[4] + ((float)data[5])/256.0;
      platform.setAngles(angle1, angle2, angle3);
    }
  }
}
