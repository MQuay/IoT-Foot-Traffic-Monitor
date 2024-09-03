#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ssl_client.h>
#include <WiFiClientSecure.h>
#include <esp_crt_bundle.h>

const int PIR = 27;               // CHANGE PIN NUMBER HERE IF YOU WANT TO USE A DIFFERENT PIN

//wifi network credentials
const char* ssid = "mq-pix8";
const char* pword = "mquaydemo";
const String laptop = "http://192.168.96.35";
const String localUrl = laptop + ":8000";        //url of the on-premise application "localApp"
const String weburl = laptop + ":5000"; //url of the web/cloud application "webapp"
const String device_name = "motion-trip";

String web_token = "";         // set at runtime
String web_pw = "";       // set at runtime

void notify_server() {
  HTTPClient https;
  if (https.begin(weburl + "/sense")) {
    https.addHeader("Content-Type", "application/json");
    https.addHeader("Authorization", "Bearer " + web_token);
    int code = https.POST("{\"device_name\":\"" + device_name + "\"}");
    if (code > 0) {
      Serial.println(https.getString());
    }
  }
}

void notify_local() {
  HTTPClient http;
  http.begin(localUrl + "/alarm");
  int code = http.GET();
  if (code > 0) {
    Serial.println(http.getString());
  }
}

void get_web_token() {
  if (WiFi.status()==WL_CONNECTED) {
    //add device to web db and get a new generated pw from local
    String res = "{}";
    HTTPClient http;
    http.begin(localUrl + "/add-device");
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST("{\"device_name\":\"" + device_name + "\"}");
    if (httpResponseCode>0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      web_pw = http.getString();
      Serial.println(web_pw);
      if (web_pw[0] != '"'){
        web_pw = "";
        Serial.print("Failed to get pw");
        return;
      }
    }
    else {
      Serial.print("Failed to get pw. Error code: ");
      Serial.println(httpResponseCode);
      http.end();
      return;
    }
    http.end();
    
    // login in to web 
    HTTPClient https;
    if (https.begin(weburl + "/login")) {
      https.addHeader("Content-Type", "application/json");
      int code = https.POST("{\"device_name\":\"" + device_name + "\",\"password\":" + web_pw + "}");
      if (code > 0) {
        String ret = https.getString();
        web_token = ret.substring(1, ret.length() - 2);
        Serial.println(web_token);
      } 
      else {
        Serial.println("Failed to get token. Error code: ");
      }
    }
    https.end();
  }
  else {
    Serial.println("WiFi no connect");
    return;
  }
}

void setup() {
  Serial.begin (19200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pword);
  
  // connect to wifi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to Wifi...");
  }
  Serial.println("Connected to Wifi network");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // init sensor pins
  pinMode(PIR, INPUT);

  get_web_token();
}

void loop() {
  if (web_token.equals("") or web_pw.equals("")) {
    get_web_token();
  }
  if (digitalRead(PIR) == HIGH) {
    Serial.println("Motion Detected");
    notify_server();
    notify_local();
    delay(5000);
  }
  else {
    delay(500);
  }
}
