# Physical Intrusion detection and foot traffic monitoring system

## Hardware Requirements:
* ESP32
* HC-SR04 Ultrasonic Distance Sensor
* AM312 mini PIR Motion Sensor

## Installation
Install all software dependencies for the respective python application using `pip install -r /path/to/backend/requirements.txt`.

Use Arduino IDE to upload code to ESP32 boards, ensuring to install the [Arduino-ESP32](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html) library and change variables containing server url, the server root certificate and wifi credentials.

Using ESP32 boards with the appropriate sensors connected, upload `distance.io` for a board with an HC-SR04 ultrasonic distance sensor and upload the `motion.ino` to a board with an AM312 mini PIR motion sensor connected.

## How to Use:
The Flask applications should be initialised and running before the ESP32 boards.
The Flask web applications can be deployed on any wsgi server or tested locally using `flask run`. See the Flask documentation [here](https://flask.palletsprojects.com/en/3.0.x/quickstart/).

Change the global variables in the arduino code to that of your own WiFi credentials, server details and sensor pins used (if applicable). Upload the Arduino code to the ESP32 boards and they should start automatically when powered on.

The entire process is autonomous, if configured properly, you should be able to 'trip' the sensors yourself and see that this has been detected at the `/intrusions` endpoint of your web application.