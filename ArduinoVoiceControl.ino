#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

unsigned long lastUpdateTime = 0;
const unsigned long idleDelay = 5000;
bool isIdle = false;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

String message = "";

int buzzerPin = 7;

String idleText = "Say: Hey Homie Buddy!";
int charIndex = 0;
bool showCursor = true;

void showIdleScreen() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 20);

  display.print(idleText.substring(0, charIndex));
  display.display();

  charIndex++;

  if (charIndex > idleText.length()) {
    delay(1000);
    charIndex = 0;
  }

  showCursor = !showCursor;
  delay(120);
}

void printWrappedText(String text) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);

  int cursorY = 0;

  int start = 0;
  while (start < text.length()) {
    int newlineIndex = text.indexOf('\n', start);
    String line;

    if (newlineIndex == -1) {
      line = text.substring(start);
      start = text.length();
    } else {
      line = text.substring(start, newlineIndex);
      start = newlineIndex + 1;
    }

    display.setCursor(0, cursorY);
    display.println(line);
    cursorY += 10;
  }

  display.display();
}

void setup() {
  Serial.begin(9600);

  pinMode(buzzerPin, OUTPUT);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for (;;)
      ;
  }

  showIdleScreen();
  lastUpdateTime = millis();
}

void loop() {
  if (Serial.available()) {
    String line1 = Serial.readStringUntil('\n');
    delay(10);  // small delay to allow next line to arrive

    String line2 = "";
    if (Serial.available()) {
      line2 = Serial.readStringUntil('\n');
    }

    if (line1 == "REMINDER!") {
      // Beep pattern
      for (int i = 0; i < 3; i++) {
        tone(buzzerPin, 1000);  // 1000 Hz
        delay(300);
        noTone(buzzerPin);
        delay(200);
      }
    }

    String fullMessage = line1 + "\n" + line2;
    printWrappedText(fullMessage);


    lastUpdateTime = millis();
    charIndex = 0;
  } else {
    if (millis() - lastUpdateTime > idleDelay) {
      showIdleScreen();
    }
  }
}
