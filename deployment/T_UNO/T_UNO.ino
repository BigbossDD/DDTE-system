#include <Servo.h>

Servo panServo;   // pin 9  – left / right
Servo tiltServo;  // pin 10 – up   / down

const int PAN_PIN  = 9;
const int TILT_PIN = 10;

const int CENTRE   = 90;   // boot position
const int STEP     = 3;    // degrees per command — tune this for speed

// Clamp helper — keeps servos inside 0–180°
int clamp(int val) {
  if (val < 0)   return 0;s
  if (val > 180) return 180;
  return val;
}

int panPos  = CENTRE;
int tiltPos = CENTRE;

void setup() {
  panServo.attach(PAN_PIN);
  tiltServo.attach(TILT_PIN);

  panServo.write(panPos);
  tiltServo.write(tiltPos);

  Serial.begin(9600);
  Serial.println("UNO ready — waiting for commands");
}

void loop() {
  if (!Serial.available()) return;

  char cmd = Serial.read();

  switch (cmd) {

    case 'L':
      panPos = clamp(panPos - STEP);
      panServo.write(panPos);
      Serial.print("Pan  L → "); Serial.println(panPos);
      break;

    case 'R':
      panPos = clamp(panPos + STEP);
      panServo.write(panPos);
      Serial.print("Pan  R → "); Serial.println(panPos);
      break;

    case 'U':
      tiltPos = clamp(tiltPos - STEP);
      tiltServo.write(tiltPos);
      Serial.print("Tilt U → "); Serial.println(tiltPos);
      break;

    case 'D':
      tiltPos = clamp(tiltPos + STEP);
      tiltServo.write(tiltPos);
      Serial.print("Tilt D → "); Serial.println(tiltPos);
      break;

    case 'S':
      // hold position — nothing to do
      Serial.println("Hold");
      break;
  }
}