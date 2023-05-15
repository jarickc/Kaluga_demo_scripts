# Introduction

This is a collection of programs that have been found to work on the kaluga dev kit version 1.3 to demonstrate the included HW.

# Setup
## Verify Operation
1. Unpack your Kaluga Dev Kit
1. Connect Speaker to the Speaker Port on the [Audio Daughter card](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s2/hw-reference/esp32s2/user-guide-esp-lyrat-8311a_v1.3.html)
1. Connect the [camera module](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s2/hw-reference/esp32s2/user-guide-esp-lyrap-cam-v1.1.html) to the camera 18 pin connector on the Kaluga main board. 
1. Connect a USB cable into the PWR port
1. Put switch in on position and verify that the Kaluga powers on, plays a flash animation and sound, and turns the camera on with displaying what the screen is pointing at.

## Setup Circuit Python
1. Strip back about 1 inch of the USB breakout cable black outer sheathing to expose a longer length of the enclosed wires.
1. Plug the USB breakout canle in as follows:
    1. White -> IO19/D-
    1. Green -> IO20/D+
    1. Black -> Gnd/Ground
    1. Red -> No Connection
1. Go to the Kaluga 1.3 CircuitPython page and select open installer. https://circuitpython.org/board/espressif_kaluga_1.3/
1. Select Full CircuitPython 8.0.5 Install (or latest version)
1. Connect and select the ESP32-S2 device.
1. Continue through prompts until it is installed.
    1. This will Erase Flash, install the Bootloader, and CircuitPython
    1. This operation takes several minutes.
1. Verify a CircuitPython Drive is now on your PC (may require hard resetting the board)

## Configure Environment
1. [Install Mu](https://codewith.mu/)
1. Ensure board is connected to the PC
1. Open Mu
1. Click Serial
1. CTRL-C
1. enter import espcamera and verify no errors

# ToDo
## Scripts
* Speaker
* Headphone
* Microphone
* Touch Controller
* TBD addon Sensors

## Documentation
* Kaluga HW overview
* Sensor addon guide
* Challenge point scoring

## Done
* Camera
* LCD
* WIFI
* Setup