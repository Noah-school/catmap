import time
import os

def check_wifi_connection():
    while True:
        response = os.system("ping -n 1 google.com")
        if response != 0:
            print("WiFi not connected. Attempting to reconnect...")
            os.system("sudo ifdown wlan0 && sudo ifup wlan0")
        else:
            print("WiFi connected!")
        time.sleep(60)

check_wifi_connection()
