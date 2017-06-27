#define PIN_1 8
#define INTERR_PIN 2
#define INTERR_NUM 0

#define WRITE_TICKS 10000

volatile boolean interr;

boolean A, B;

int8_t d1, d2;

int ticks;

void setup() {
    Serial.begin(9600);
    pinMode(PIN_1, INPUT_PULLUP);
    pinMode(INTERR_PIN, INPUT_PULLUP);
    attachInterrupt(INTERR_NUM, manageInterr, RISING);
    ticks = 0;
    d1 = d2 = 0;
}


void loop() {
    if(interr) {
        A = digitalRead(INTERR_PIN);
        B = digitalRead(PIN_1);
        if(A && B) ++d1;
        if(A && !B) --d1;
        interr = 0;
    }
    
    ++ticks;
    if(ticks == WRITE_TICKS) {
        ticks = 0;
        Serial.print(d1);
        Serial.print(" ");
        Serial.println(d2);
        d1 = 0;
    }
}

void manageInterr() {
    interr = 1;
}
