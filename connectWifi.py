import os

def get_wifi_credentials():
    ssid = input("Enter WiFi SSID: ")
    password = input("Enter WiFi Password: ")

    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
        f.write(
            f"""
network={{
    ssid="{ssid}"
    psk="{password}"
    priority=1
}}
"""
        )

    os.system("sudo wpa_cli reconfigure")

get_wifi_credentials()
