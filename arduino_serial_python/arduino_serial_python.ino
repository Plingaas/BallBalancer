#include <Servo.h>

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];   // temporary array for use when parsing

int servoPosArray[3];    // variables to hold the parsed data
boolean newData = false;

int target1 = 0;
int target2 = 0;
int target3 = 0;

Servo servo1;
Servo servo2;
Servo servo3;

Platform platform;
void setup() {
    Serial.begin(250000);
    Serial.println("This program expects 3 integers");
    Serial.println("Enter the angles formated like this (35, -12, 24)  ");
    Serial.println();
    Serial.setTimeout(0);

    pinMode(18, OUTPUT);
    pinMode(19, OUTPUT);
    pinMode(21, OUTPUT);
    pinMode(22, OUTPUT);
    pinMode(23, OUTPUT);
    pinMode(34, OUTPUT);
    pinMode(12, OUTPUT);
    pinMode(13, OUTPUT);
    pinMode(14, OUTPUT);

    digitalWrite(21, HIGH); // en pins
    digitalWrite(34, HIGH);
    digitalWrite(14, HIGH);

    servo1.attach(9);
    servo2.attach(10);
    servo3.attach(11);

    servo1.write(90);
    servo2.write(90);
    servo3.write(90);
    platform.reset();
    platform.setAngles(50, 50, 50);
}

unsigned long prevTime = micros();
unsigned long dt = 0;
unsigned long now = micros();
void loop() {
    now = micros();
    dt = now-prevTime;
    recvWithStartEndMarkers();
    if (newData == true) {
        strcpy(tempChars, receivedChars);
            //this temporary copy is necessary to protect the original data
            //because strtok() used in parseData() replaces the commas with \0
        parseData();
        useParsedData();
        newData = false;
    }
  platform.update(dt);
  servo1.write(platform.stepper1.currentPosition/71.111);
  Serial.println(platform.stepper1.currentPosition);
  //servo2.write(platform.stepper2.target/71.11111);
  //servo3.write(platform.stepper3.target/71.11111);
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '(';
    char endMarker = ')';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void parseData() {      //split serial-data into parts

    char * strtokIndx; //this is used by strtok() as an index

    strtokIndx = strtok(tempChars,","); //get the first value from the Serial-string 
    servoPosArray[0] = atoi(strtokIndx); //copy it to the positionarray
 
    strtokIndx = strtok(NULL, ","); //this continues where the previous call left off
    servoPosArray[1] = atoi(strtokIndx); //adds 2nd value to positionarray

    strtokIndx = strtok(NULL, ",");
    servoPosArray[2] = atoi(strtokIndx); //adds 3rd value to positionarray
}

void useParsedData() {
    platform.stepper1.target = servoPosArray[0] + 90; //add 90 degrees to rotate the servo around its midpoint
    platform.stepper2.target = servoPosArray[1] + 90;
    platform.stepper3.target = servoPosArray[2] + 90;
}
