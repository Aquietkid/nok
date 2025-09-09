#include <WiFi.h>
#include <WiFiClient.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>

//function headers
void setup();
void loop();
void sendRequestAndControlServo();

// WiFi credentials
const char* ssid = "111 Jinnah ";
const char* password = "ManaManayManiMano";

// External API endpoint (dummy for now)
const char* apiURL = "http://192.168.1.9:5000/check"; // replace with your PC IP
Servo doorServo;
const int servoPin = 18;
const int buzzerPin = 19;
const int lockedPosition = 0;
const int unlockedPosition = 90;

const int buttonPin = 4;
unsigned long lastPress = 0;
const unsigned long cooldown = 2000; // ms

void setup() {
  Serial.begin(115200);

  doorServo.attach(servoPin);
  doorServo.write(lockedPosition);

  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(buzzerPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP); // Button pressed = LOW

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP: " + WiFi.localIP().toString());
}

void loop() {
  if (digitalRead(buttonPin) == LOW) {
    digitalWrite(buzzerPin, HIGH);  // Buzzer on
    unsigned long now = millis();
    if (now - lastPress > cooldown) {
      lastPress = now;
      Serial.println("Button pressed! Sending request...");
      sendRequestAndControlServo();
    }
  } else {
    digitalWrite(buzzerPin, LOW);   // Buzzer off
  }
}

void sendRequestAndControlServo() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(apiURL);
    int httpCode = http.GET();

    if (httpCode == 200) {
      String payload = http.getString();
      Serial.println("Response: " + payload);

      // Parse JSON
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (!error) {
        const char* result = doc["result"];  // "yes" or "no"
        if (strcmp(result, "yes") == 0) {
          doorServo.write(unlockedPosition);
          Serial.println("Servo -> UNLOCK");
        } else {
          doorServo.write(lockedPosition);
          Serial.println("Servo -> LOCK");
        }
      } else {
        Serial.println("JSON parse error!");
      }
    } else {
      Serial.printf("Request failed, code: %d\n", httpCode);
    }

    http.end();
  } else {
    Serial.println("WiFi not connected!");
  }
}