#include <Servo.h>

Servo panServo;
Servo tiltServo;

const int PAN_PIN  = 9;
const int TILT_PIN = 10;

int panPos  = 90;
int tiltPos = 90;

String input = "";

void setup() {
  panServo.attach(PAN_PIN);
  tiltServo.attach(TILT_PIN);

  panServo.write(panPos);
  tiltServo.write(tiltPos);

  Serial.begin(9600);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      // parse "pan,tilt"
      int commaIndex = input.indexOf(',');

      if (commaIndex > 0) {
        int newPan  = input.substring(0, commaIndex).toInt();
        int newTilt = input.substring(commaIndex + 1).toInt();

        // clamp
        newPan  = constrain(newPan,  0, 180);
        newTilt = constrain(newTilt, 0, 180);

        panServo.write(newPan);
        tiltServo.write(newTilt);

        Serial.print("Pan: "); Serial.print(newPan);
        Serial.print(" | Tilt: "); Serial.println(newTilt);
      }

      input = "";  // reset buffer
    } else {
      input += c;
    }
  }
}