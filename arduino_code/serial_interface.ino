const int sensorPin=3;
const int sensorPintwo=5;
const int ledPinred= 1;
const int ledPinyellow= 4;
const int ledPingreen= 6;


int count = 0;
String inByte;
void setup()
{

Serial.begin(4800); // start the serial terminal
Serial.println();

pinMode(ledPinred, OUTPUT);
pinMode(ledPinyellow, OUTPUT);
pinMode(ledPingreen, OUTPUT);
digitalWrite(4, HIGH);

}

void loop()
{
  int val= analogRead(sensorPin);
  Serial.print(val);
  Serial.print(' ');
  Serial.println();

  if(Serial.available()) // if data available in serial port
    {
      inByte = Serial.readStringUntil('\n'); // read data until newline
      if(inByte == "Low")
      {
      digitalWrite(4, LOW);
      digitalWrite(6, HIGH);
      }
    }
}

