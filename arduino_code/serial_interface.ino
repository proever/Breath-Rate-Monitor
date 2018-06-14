const int sensorPin=3;
const int sensorPintwo=5;
const int ledPinHigh= 2;
const int ledPinGreen= 4;
const int ledPinLow= 6;


int count = 0;
String inByte;
void setup()
{

Serial.begin(4800); // start the serial terminal
Serial.println();

pinMode(ledPinHigh, OUTPUT);
pinMode(ledPinGreen, OUTPUT);
pinMode(ledPinLow, OUTPUT);
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
      digitalWrite(ledPinGreen, LOW);
      digitalWrite(ledPinLow, HIGH);
      digitalWrite(ledPinHigh, LOW);
      }
      else if(inByte == "Green")
      {
      digitalWrite(ledPinGreen, HIGH);
      digitalWrite(ledPinLow, LOW);
      digitalWrite(ledPinHigh, LOW);
      }
      if(inByte == "High")
      {
      digitalWrite(ledPinGreen, LOW);
      digitalWrite(ledPinLow, LOW);
      digitalWrite(ledPinHigh, HIGH);
      }
    }
}

