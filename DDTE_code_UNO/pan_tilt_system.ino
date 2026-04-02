// this code activated the servos and the pan tilt system 
//note pan is at 9 and tilt is at 10 

//#include <Servo.h>

//Servo panServo;   // left / right
//Servo tiltServo;  // up   / down

// Centre position for a 180° servo
const int CENTRE = 90;
const int DELAY  = 600;   // ms between moves — lower = faster test

void setup() {
  // panServo.attach(9);
  // tiltServo.attach(10);

  //Serial.begin(9600);
  //Serial.println("Drone tracker — servo test starting");

  // Move both to centre on boot
  //panServo.write(CENTRE);
  //tiltServo.write(CENTRE);
  //delay(1000);
}

void loop() {

  // ── Pan test (left / right) ──────────────────────────
  //Serial.println("Pan LEFT");
  //panServo.write(45);       // left
  //delay(DELAY);

  //Serial.println("Pan CENTRE");
  //panServo.write(CENTRE);
  //delay(DELAY);

  //Serial.println("Pan RIGHT");
  //panServo.write(135);      // right
  //delay(DELAY);

  //Serial.println("Pan CENTRE");
  //panServo.write(CENTRE);
  //delay(DELAY);

  // ── Tilt test (up / down) ────────────────────────────
  //Serial.println("Tilt UP");
  //tiltServo.write(45);      // up
  //delay(DELAY);

  //Serial.println("Tilt CENTRE");
  //tiltServo.write(CENTRE);
  //delay(DELAY);

  //Serial.println("Tilt DOWN");
  //tiltServo.write(135);     // down
  //delay(DELAY);

  //Serial.println("Tilt CENTRE");
  //tiltServo.write(CENTRE);
  //delay(DELAY);

  //Serial.println("── cycle complete ──");
  //delay(1500);
}