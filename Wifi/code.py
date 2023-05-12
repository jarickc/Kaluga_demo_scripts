# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests

# URLs to fetch from
URL = "http://wifitest.adafruit.com/testwifi/index.html"
NumberURL = "http://numbersapi.com/random/math?json"
BoredURL = "http://www.boredapi.com/api/activity?type=recreational"
# Get wifi credentials from credentials.py file
try:
    from credentials import credentials
except ImportError:
    print("WiFi credentials are kept in credentials.py. Please update yours only on your circuitpython drive. Do not commit this file to public repositories")
    raise

print("ESP32-S2 Wifi Test")

print("MAC addr:", [hex(i) for i in wifi.radio.mac_address])

print("Local WiFi networks:")
for network in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
            network.rssi, network.channel))
wifi.radio.stop_scanning_networks()

print("Connecting to %s"%credentials["ssid"])
wifi.radio.connect(credentials["ssid"], credentials["password"])
print("Connected to %s!"%credentials["ssid"])
print("IP address is", wifi.radio.ipv4_address)

ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

print("Fetching math fact about a random number from", NumberURL)
response = requests.get(NumberURL)
print("-" * 40)
print("The fact for ", response.json()["number"], ": ", response.json()["text"])
print("-" * 40)

print("If you're getting bored and need some inpiration:")
response = requests.get(BoredURL)
print("-" * 40)
print(response.json()["activity"])
print("-" * 40)

print("done")
