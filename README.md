
![cat](https://gcdnb.pbrd.co/images/8PQyMeaTRVT1.png?o=1)


# Catmap

A small scanning device for educational purposes. Which currently can only do a select few things but i want it to cross refrence the port information with searchsploit later in the future.


## prerequisite
specs:
- raspberry pi zero 2 w 
- waveshare 2.13 v3 E-ink display
- any power  source

Warning if this has not been tested on other hardware
- Experiment at your own risk
- if you do decide to try tinkering with this you can start by changing this lib for your display:
```python 
    ./main.py
    line 20: epd = epd2in13_V4.EPD()
```
## Installation guide for the raspberry pi zero 2 w 

quick install:
```bash
  git clone https://github.com/Noah-school/catmap
  cd catmap
  pip install -r requirements.txt
```

Make a file with startup rules: 
(replace <name> with current user)
```bash
sudo nano /etc/systemd/system/catmap.service
```
```bash
[Unit]
Description=Run ip.py on boot
After=network.target

[Service]
ExecStartPre=/bin/sleep 30
ExecStart=/usr/bin/python3 /home/<name>/kitmap/ip.py
WorkingDirectory=/home/<name>/kitmap
User=<name>
Group=<name>
Restart=no
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```
After that save the file and enable it like this:
```bash
sudo systemctl enable catmap
sudo systemctl start catmap
```

Use this command check if everything works:
```bash
sudo systemctl status catmap
```

## Run without hardware

quick install:
```bash
  git clone https://github.com/Noah-school/catmap
  cd catmap
  pip install -r requirements.txt
```
Run a simulation without hardware:
```bash
  python main.py --simulate
```
You can view the image at "./output/epd_image.png"
Keep in mind the image will change every frame. I used vscode to view it without reopening the file to see each frame. Im still working on how to compile to gif or mp4 but it will compromise the reason for the screen.


## Usage
Run digital simulation:
```bash
  python main.py
```
optional settings:
```bash
Usage: main.py [OPTIONS]

Options:
  --simulate      Simulate the display (no hardware required)
  --network TEXT  Network range to scan (default: 192.168.0.0/24)  [default:
                  192.168.0.0/24]
  --ports TEXT    Comma-separated list of ports to scan (default: common
                  ports)  [default: 22,21,80,8080,3000,5000,6666,443,3389,23,2
                  5,53,110,143,445,5900,2375,3306,6379,27017]
  --help          Show this message and exit.
```

## Outputs
all outputs will be dumped in the "./output" folder.
this folder contains
####
errors.log:
```bash
example:
2024-12-12 23:46:09,248 - ERROR - Error updating display: cannot open resource
2024-12-12 23:46:11,249 - ERROR - Error updating display: cannot open resource
2024-12-12 23:46:13,251 - ERROR - Error updating display: cannot open resource
```
####
online_ips_ports.txt:
```bash
example:
Host: 10.0.7.27
Ports: 23, 80, 8080

Host: 10.0.10.2
Ports: 22, 53 
```
epd_image.png: (emulated display)
####
![example](https://gcdnb.pbrd.co/images/1K0QjAhc512K.png?o=1)
## Screenshots

![example](https://gcdnb.pbrd.co/images/uVqVjlZZubs5.jpg?o=1)


## Acknowledgement

 - [waveshareteam E-paper repo](https://github.com/waveshareteam/e-Paper)


