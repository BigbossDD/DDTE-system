void setup() {
  pinMode(13, OUTPUT);   // built-in LED
  Serial.begin(9600);
}

void loop() {

  if (Serial.available() > 0) {

    char data = Serial.read();

    digitalWrite(13, HIGH);
    delay(200);
    digitalWrite(13, LOW);

  }
}