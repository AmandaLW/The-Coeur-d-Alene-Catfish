#include <Wire.h>

#define SLAVE_ADDRESS 0x04
int analogPin = 3;
int command = 0;
int reading = 0;
byte buf[2];

void setup() {
  // turn on LED
  pinMode(13, OUTPUT);

  // start serial for output
  Serial.begin(9600);
  
  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);

  // define callbacks for i2c communication
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);

  // we're ready to go
  Serial.println("Ready!");
}

void loop() {
  delay(100);
}

// callback for received data
void receiveData(int byteCount) {
  while (Wire.available()) {
    command = Wire.read();
    Serial.print("command received: ");
    Serial.println(command);

    if (command == 1) {
      Serial.println("updating analog reading");
      reading = analogRead(analogPin);
    }
    else {
      Serial.print("ignoring unknown command: ");
      Serial.println(command);
    }
  }
}

// callback for sending data
void sendData() {
  buf[0] = reading & 0xFF;
  buf[1] = (reading & 0xFF00) >> 8;
  
  Serial.print("sending: ");
  Serial.println(reading);
  Wire.write(buf, 2);
}

