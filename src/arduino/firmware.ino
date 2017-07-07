#define WRITE_TICKS 100

void setup() {
    Serial.begin(9600);
    pinMode(A0, INPUT);
    pinMode(A1, INPUT);
    pinMode(A2, INPUT);
}

int ticks = 0;

long ch1_avg_sum = 0;
int ch1_old = 0;

long ch2_avg_sum = 0;
int ch2_old = 0;

long ch3_avg_sum = 0;
int ch3_old = 0;

void loop() {
    
    ch1_avg_sum += analogRead(A0);
    ch2_avg_sum += analogRead(A1);
    ch3_avg_sum += analogRead(A2);

    ++ticks;
    if(ticks == WRITE_TICKS) {
        int ch1_new = ch1_avg_sum/WRITE_TICKS;
        int ch2_new = ch2_avg_sum/WRITE_TICKS;
        int ch3_new = ch3_avg_sum/WRITE_TICKS;
        
        Serial.print(ch1_new-ch1_old);
        Serial.print(" ");
        Serial.print(ch2_new-ch2_old);
        Serial.print(" ");
        Serial.println(ch3_new-ch3_old);
        
        ch1_avg_sum = 0;
        ch1_old = ch1_new;
        ch2_avg_sum = 0;
        ch2_old = ch2_new;
        ch3_avg_sum = 0;
        ch3_old = ch3_new;
        
        ticks = 0;
    }
}