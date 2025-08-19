#define relay1 2  
#define relay2 3  
#define relay3 7  
#define relay4 8 

char voice[32];  // Buffer for serial input

void setup() {
  Serial.begin(9600);
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  pinMode(relay3, OUTPUT);
  pinMode(relay4, OUTPUT);
  switchoff();  // Ensure all relays are off at startup
}

void loop() {
  if (Serial.available()) {
    delay(10);  
    int i = 0;
    while (Serial.available()) {
      char c = Serial.read();
      if (c == '#' || i >= 31) {  
        voice[i] = '\0';  
        break;
      }
      voice[i++] = c;
    }
    
    Serial.println(voice);

    if (strcmp(voice, "A") == 0) {
      switchon();
    } else if (strcmp(voice, "a") == 0) {
      switchoff();
    } else if (strcmp(voice, "B") == 0) {
      digitalWrite(relay1, LOW);
    } else if (strcmp(voice, "b") == 0) {
      digitalWrite(relay1, HIGH);
    } else if (strcmp(voice, "C") == 0) {
      digitalWrite(relay2, LOW);
    } else if (strcmp(voice, "c") == 0) {
      digitalWrite(relay2, HIGH);
    } else if (strcmp(voice, "D") == 0) {
      digitalWrite(relay3, LOW);
    } else if (strcmp(voice, "d") == 0) {
      digitalWrite(relay3, HIGH);
    } else if (strcmp(voice, "E") == 0) {
      digitalWrite(relay4, LOW);
    } else if (strcmp(voice, "e") == 0) {
      digitalWrite(relay4, HIGH);
    }
  }
}

void switchon() {
  digitalWrite(relay1, LOW);
  digitalWrite(relay2, LOW);
  digitalWrite(relay3, LOW);
  digitalWrite(relay4, LOW);
}

void switchoff() {
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
  digitalWrite(relay3, HIGH);
  digitalWrite(relay4, HIGH);
}