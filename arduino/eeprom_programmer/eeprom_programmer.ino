const int PIN_DATA0 = 2;
const int PIN_DATA1 = 3;
const int PIN_DATA2 = 4;
const int PIN_DATA3 = 5;
const int PIN_DATA4 = 6;
const int PIN_DATA5 = 7;
const int PIN_DATA6 = 8;
const int PIN_DATA7 = 9;
const int PIN_NWE = 10;
const int PIN_NOE = 11;
const int PIN_RESET = 12;
const int PIN_CLK = 13;
const int PIN_RDY = A0;


void setup() {
  Serial.begin(9600);
  digitalWrite(PIN_NWE, HIGH);
  digitalWrite(PIN_NOE, HIGH);
  digitalWrite(PIN_CLK, LOW);
  digitalWrite(PIN_RESET, LOW);
  pinMode(PIN_NOE, OUTPUT);
  pinMode(PIN_NWE, OUTPUT);
  pinMode(PIN_CLK, OUTPUT);
  pinMode(PIN_RESET, OUTPUT);
  pinMode(PIN_RDY, INPUT_PULLUP);
  pinMode(PIN_DATA0, INPUT_PULLUP);
  pinMode(PIN_DATA1, INPUT_PULLUP);
  pinMode(PIN_DATA2, INPUT_PULLUP);
  pinMode(PIN_DATA3, INPUT_PULLUP);
  pinMode(PIN_DATA4, INPUT_PULLUP);
  pinMode(PIN_DATA5, INPUT_PULLUP);
  pinMode(PIN_DATA6, INPUT_PULLUP);
  pinMode(PIN_DATA7, INPUT_PULLUP);
}

unsigned int counter = 0;

void advance_counter() {
  counter += 1;
  digitalWrite(PIN_CLK, counter & 1);
}

unsigned char read_byte() {
  digitalWrite(PIN_NOE, LOW);
  delayMicroseconds(500);

  unsigned char x = digitalRead(PIN_DATA0) |
      (digitalRead(PIN_DATA1) << 1) |
      (digitalRead(PIN_DATA2) << 2) |
      (digitalRead(PIN_DATA3) << 3) |
      (digitalRead(PIN_DATA4) << 4) |
      (digitalRead(PIN_DATA5) << 5) |
      (digitalRead(PIN_DATA6) << 6) |
      (digitalRead(PIN_DATA7) << 7);

  digitalWrite(PIN_NOE, HIGH);
  // Done by caller now
  //advance_counter();
  return x;
}

void write_byte(unsigned char x) {
  // Assumes NOE is high already

  digitalWrite(PIN_DATA0, (x >> 0) & 1);
  digitalWrite(PIN_DATA1, (x >> 1) & 1);
  digitalWrite(PIN_DATA2, (x >> 2) & 1);
  digitalWrite(PIN_DATA3, (x >> 3) & 1);
  digitalWrite(PIN_DATA4, (x >> 4) & 1);
  digitalWrite(PIN_DATA5, (x >> 5) & 1);
  digitalWrite(PIN_DATA6, (x >> 6) & 1);
  digitalWrite(PIN_DATA7, (x >> 7) & 1);

  pinMode(PIN_DATA0, OUTPUT);
  pinMode(PIN_DATA1, OUTPUT);
  pinMode(PIN_DATA2, OUTPUT);
  pinMode(PIN_DATA3, OUTPUT);
  pinMode(PIN_DATA4, OUTPUT);
  pinMode(PIN_DATA5, OUTPUT);
  pinMode(PIN_DATA6, OUTPUT);
  pinMode(PIN_DATA7, OUTPUT);

  delayMicroseconds(1000);

  digitalWrite(PIN_NWE, LOW);

  delayMicroseconds(1000);

  digitalWrite(PIN_NWE, HIGH);

  // Testing: wait for a sufficient amount of time
  delay(10);
  // Wait for low pulse on RDY pin
  //while(digitalRead(PIN_RDY) == HIGH);
  //while(digitalRead(PIN_RDY) == LOW);

  pinMode(PIN_DATA0, INPUT_PULLUP);
  pinMode(PIN_DATA1, INPUT_PULLUP);
  pinMode(PIN_DATA2, INPUT_PULLUP);
  pinMode(PIN_DATA3, INPUT_PULLUP);
  pinMode(PIN_DATA4, INPUT_PULLUP);
  pinMode(PIN_DATA5, INPUT_PULLUP);
  pinMode(PIN_DATA6, INPUT_PULLUP);
  pinMode(PIN_DATA7, INPUT_PULLUP);

  // Done by caller now
  //advance_counter();
}

void reset_counter() {
  counter = 0;
  digitalWrite(PIN_CLK, LOW);
  digitalWrite(PIN_RESET, HIGH);
  delay(10);
  digitalWrite(PIN_RESET, LOW);
}

word checksum(word a0, word a1) {
  word sum = 0xabba;
  word x;
  reset_counter();
  for (int i=0; i<a0; i++) advance_counter();
  for (int i=a0; i<a1; i++) {
    x = read_byte();
    advance_counter();
    sum += (sum << 3) + (sum << 9) + x;
  }
  return sum;
}

int data;
char buf[3];
word cs;

void loop() {
  data = Serial.read();
  if (data != -1) {
    switch (data) {
      case 'R':
        reset_counter();
        break;
      case 'W':
        while ((data = Serial.read()) == -1) ;
        buf[0] = data;
        while ((data = Serial.read()) == -1) ;
        buf[1] = data;
        buf[2] = 0;
        data = strtol(buf, NULL, 16);
        write_byte(data);
        data = read_byte();
        advance_counter();
        Serial.write('W');
        Serial.print(data, HEX);
        Serial.write('\n');
        break;
      case 'L':
        data = read_byte();
        advance_counter();
        Serial.write('L');
        Serial.print(data, HEX);
        Serial.write('\n');
        break;
      case 'S':
        cs = checksum(0, 0x2000);
        Serial.write('S');
        Serial.print(cs, HEX);
        Serial.write('\n');
        break;
      default:
        Serial.write(data);
        Serial.write('?');
        Serial.write('\n');
        break;
    }
  }
}

