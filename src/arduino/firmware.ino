#define WRITE_TICKS 100

void setup() {
    Serial.begin(9600);
    pinMode(A0, INPUT);
    pinMode(A1, INPUT);
    pinMode(A2, INPUT);
}

int ticks = 0;

long ch1_avg_sum = 0;
long ch2_avg_sum = 0;
long ch3_avg_sum = 0;

void loop() {
    
    ch1_avg_sum += analogRead(A0);
    ch2_avg_sum += analogRead(A1);
    ch3_avg_sum += analogRead(A2);

    ++ticks;
    if(ticks == WRITE_TICKS) {
        int ch1 = ch1_avg_sum/WRITE_TICKS;
        int ch2 = ch2_avg_sum/WRITE_TICKS;
        int ch3 = ch3_avg_sum/WRITE_TICKS;
        
        Serial.print(ch1);
        Serial.print(" ");
        Serial.print(ch2);
        Serial.print(" ");
        Serial.println(ch3);
        
        ch1_avg_sum = 0;
        ch2_avg_sum = 0;
        ch3_avg_sum = 0;
        
        ticks = 0;
    }
}