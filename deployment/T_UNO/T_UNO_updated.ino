#include <Servo.h>

Servo servoPan;
Servo servoTilt;

int pan = 70;
int tilt = 40;

String input = "";

void setup() {
  Serial.begin(9600);

  servoPan.attach(9);
  servoTilt.attach(10);

  servoPan.write(pan);
  servoTilt.write(tilt);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      processCommand(input);
      input = "";
    } else {
      input += c;
    }
  }
}

void processCommand(String cmd) {
  int commaIndex = cmd.indexOf(',');

  if (commaIndex == -1) return;

  int newPan  = cmd.substring(0, commaIndex).toInt();
  int newTilt = cmd.substring(commaIndex + 1).toInt();

  // smooth movement (important!)
  pan  = constrain(newPan,  10, 170);
  tilt = constrain(newTilt, 10, 160);

  servoPan.write(pan);
  servoTilt.write(tilt);
}