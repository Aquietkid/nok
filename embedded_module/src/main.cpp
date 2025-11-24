#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <WiFi.h>
#include <WiFiClient.h>

void setup();
void loop();
void sendRequestAndControlServo();
void handleOpen();
void handleClose();

const char *ssid = "POCO X3 Pro";
const char *password = "HelloWorlds";
const char *apiURL = "http://10.126.43.213:5000/check";

// const char *ssid = "111 Jinnah "; 
// const char *password = "ManaManayManiMano"; 
// const char *apiURL = "http://192.168.1.11:5000/check"; // home wifi

Servo doorServo;
const int servoPin = 18;
const int buzzerPin = 19;
const int lockedPosition = 120;
const int unlockedPosition = 0;
const int buttonPin = 4;

unsigned long lastPress = 0;
const unsigned long cooldown = 2000;
unsigned long unlockTime = 0;
bool isUnlocked = false;

WebServer server(80);

void handleOpen() {
  doorServo.write(unlockedPosition);
  isUnlocked = true;
  unlockTime = millis();

  StaticJsonDocument<100> doc;
  doc["status"] = "opened";

  String res;
  serializeJson(doc, res);
  server.send(200, "application/json", res);
}

void handleClose() {
  doorServo.write(lockedPosition);
  isUnlocked = false;

  StaticJsonDocument<100> doc;
  doc["status"] = "closed";

  String res;
  serializeJson(doc, res);
  server.send(200, "application/json", res);
}

void setup() {
  Serial.begin(115200);
  doorServo.attach(servoPin);
  doorServo.write(lockedPosition);

  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(buzzerPin, OUTPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP: " + WiFi.localIP().toString());

  server.on("/open", HTTP_GET, handleOpen);
  server.on("/close", HTTP_GET, handleClose);
  server.begin();
}

void loop() {
  server.handleClient();

  if (digitalRead(buttonPin) == LOW) {
    // digitalWrite(buzzerPin, HIGH);
    unsigned long now = millis();
    if (now - lastPress > cooldown) {
      lastPress = now;
      Serial.println("Button pressed! Sending request...");
      sendRequestAndControlServo();
    }
  } else {
    digitalWrite(buzzerPin, LOW);
  }

  if (isUnlocked && millis() - unlockTime >= 10000) {
    doorServo.write(lockedPosition);
    isUnlocked = false;
    Serial.println("Auto-locked after 10s");
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

      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (!error) {
        const char *result = doc["result"];
        if (strcmp(result, "yes") == 0) {
          doorServo.write(unlockedPosition);
          unlockTime = millis();
          isUnlocked = true;
          Serial.println("Servo -> UNLOCK (auto-lock in 10s)");
        } else {
          doorServo.write(lockedPosition);
          isUnlocked = false;
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
