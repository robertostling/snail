const int PIN_CLK = 13;
const int PIN_X = 2;
const int PIN_SHX = 3;
const int PIN_TINH = 4;
const int PIN_NLDT = 5;
const int PIN_A = 6;
const int PIN_SHA = 7;
const int PIN_NBUF = 8;
const int PIN_WE = 9;
const int PIN_NOE = 10;
const int PIN_DATA0 = 11;
const int PIN_DATA1 = 12;
const int PIN_DATA2 = A0;
const int PIN_DATA3 = A1;
const int PIN_DATA4 = A2;
const int PIN_DATA5 = A3;
const int PIN_DATA6 = A4;
const int PIN_DATA7 = A5;

void setup() {
  Serial.begin(9600);
  digitalWrite(PIN_CLK, HIGH);
  digitalWrite(PIN_NBUF, HIGH);
  digitalWrite(PIN_NOE, HIGH);
  digitalWrite(PIN_WE, LOW);
  digitalWrite(PIN_TINH, HIGH);
  digitalWrite(PIN_NLDT, HIGH);
  pinMode(PIN_CLK, OUTPUT);
  pinMode(PIN_X, OUTPUT);
  pinMode(PIN_SHX, OUTPUT);
  pinMode(PIN_TINH, OUTPUT);
  pinMode(PIN_NLDT, OUTPUT);
  pinMode(PIN_A, OUTPUT);
  pinMode(PIN_SHA, OUTPUT);
  pinMode(PIN_NBUF, OUTPUT);
  pinMode(PIN_WE, OUTPUT);
  pinMode(PIN_NOE, OUTPUT);
  pinMode(PIN_DATA0, INPUT_PULLUP);
  pinMode(PIN_DATA1, INPUT_PULLUP);
  pinMode(PIN_DATA2, INPUT_PULLUP);
  pinMode(PIN_DATA3, INPUT_PULLUP);
  pinMode(PIN_DATA4, INPUT_PULLUP);
  pinMode(PIN_DATA5, INPUT_PULLUP);
  pinMode(PIN_DATA6, INPUT_PULLUP);
  pinMode(PIN_DATA7, INPUT_PULLUP);
}

void clock(int t) {
  delay(t);
  digitalWrite(PIN_CLK, LOW);
  delay(t);
  digitalWrite(PIN_CLK, HIGH);
}

unsigned char get_d() {
  return digitalRead(PIN_DATA0) |
      (digitalRead(PIN_DATA1) << 1) |
      (digitalRead(PIN_DATA2) << 2) |
      (digitalRead(PIN_DATA3) << 3) |
      (digitalRead(PIN_DATA4) << 4) |
      (digitalRead(PIN_DATA5) << 5) |
      (digitalRead(PIN_DATA6) << 6) |
      (digitalRead(PIN_DATA7) << 7);
}

void set_x(unsigned short n, int t) {
  digitalWrite(PIN_SHX, HIGH);
  for (int i=0; i<16; i++) {
    digitalWrite(PIN_X, (n >> i) & 1);
    clock(t);
  }
  digitalWrite(PIN_SHX, LOW);
}

void set_a(unsigned short n, int t) {
  digitalWrite(PIN_SHA, HIGH);
  for (int i=0; i<16; i++) {
    digitalWrite(PIN_A, (n >> i) & 1);
    clock(t);
  }
  digitalWrite(PIN_SHA, LOW);
}

void write_byte(unsigned short adr, unsigned short d, int t) {
  set_a(adr, t);
  set_x(d << 8, t);
  digitalWrite(PIN_WE, HIGH);

  //clock(t);
  delay(t);
  digitalWrite(PIN_CLK, LOW);
  delay(t);
  unsigned char dbus = get_d();
  digitalWrite(PIN_CLK, HIGH);

  digitalWrite(PIN_WE, LOW);

  Serial.print("WRITE ");  
  Serial.print(dbus, HEX);
  Serial.println();
}

unsigned char read_t(int t) {
  unsigned char x = 0;
  digitalWrite(PIN_TINH, LOW);
  for(int i=0; i<8; i++) {
    x |= digitalRead(PIN_DATA0) << i;
    clock(t);
  }
  digitalWrite(PIN_TINH, HIGH);
  return x;
}

unsigned char read_byte(unsigned short adr, int t) {
  set_a(adr, t);
  digitalWrite(PIN_NOE, LOW);
  digitalWrite(PIN_NLDT, LOW);
  delay(t);
  unsigned char dbus = get_d();
  digitalWrite(PIN_NLDT, HIGH);
  digitalWrite(PIN_NOE, HIGH);

/*
  delay(t);
  digitalWrite(PIN_CLK, LOW);
  delay(t);
  unsigned char dbus = get_d();
  digitalWrite(PIN_CLK, HIGH);

  digitalWrite(PIN_NOE, HIGH);
  digitalWrite(PIN_TINH, HIGH);
  digitalWrite(PIN_NLDT, HIGH);
*/
  Serial.print("READ ");  
  Serial.print(dbus, HEX);
  Serial.println();

  return read_t(t);
}

int iter = 0;

/*
TODO:

1. consider implications of NLDT being asynchronous (tie directly to NOE? -- maybe dangerous if address bus changes earlier)
2. finalize list of output signals
3. build any remaining output signal logic
4. build EEPROM programmer (remove other Arduino from DDS...)
5. add EEPROMs + latch, while making Arduino able to take over for debugging

*/

void loop() {
  delay(1000);
  write_byte(0x1234, 0x3a, 10);
  write_byte(0x4321, 0x81, 10);
  //write_byte(0x1234, 0xff, 10);
  //write_byte(0x4321, 0x00, 10);

  unsigned char b1 = read_byte(0x1234, 10);
  unsigned char b2 = read_byte(0x4321, 10);
  Serial.print("BYTES ");
  Serial.print(b1, HEX);
  Serial.print(" ");
  Serial.print(b2, HEX);
  Serial.println();

  delay(10000);

  //set_a(iter << 3, 50);
  //iter++;
  //Serial.print("DATA ");
  //Serial.print(get_d(), HEX);
  //Serial.println();
}

