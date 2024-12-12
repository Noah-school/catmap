import time
from PIL import Image, ImageDraw, ImageFont
from collections import deque
import nmap
import concurrent.futures
import logging
import click

from simulate_eink import SimulatedEPD

logging.basicConfig(filename='./output/errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_display(simulate=True):
    try:
        if simulate:
            return SimulatedEPD()
        else:
            from waveshare_epd import epd2in13_V4
            epd = epd2in13_V4.EPD()
            epd.init()
            return epd
    except Exception as e:
        logging.error(f"Error initializing display: {e}")
        raise

def update_display(epd, image, text_styles, full_refresh=False):
    try:
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, epd.width, epd.height), fill=0)

        for style in text_styles:
            text = style['text']
            position = style['position']
            font_size = style['font_size']
            try:
                if epd.width == 122 and epd.height == 250:
                    font = ImageFont.load_default()
                else:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except IOError:
                logging.error("Error loading font:  using default font")
                font = ImageFont.load_default()

            draw.text(position, text, font=font, fill=255)

        epd.displayPartial(epd.getbuffer(image))
        if full_refresh:
            epd.display(epd.getbuffer(image))
        else:
            epd.displayPartial(epd.getbuffer(image))
    except Exception as e:
        logging.error(f"Error updating display: {e}")


def get_online_hosts(network):
    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=network, arguments='-sn')
        online_hosts = [host for host in nm.all_hosts() if nm[host].state() == "up"]
        return online_hosts
    except Exception as e:
        logging.error(f"Error getting online hosts: {e}")
        return []


def log_ip_and_ports(ip, open_ports):
    try:
        with open('./output/online_ips_ports.txt', 'a') as f:
            f.write(f"Host: {ip}\n")
            f.write(f"Ports: {', '.join(map(str, open_ports))}\n\n")
    except Exception as e:
        logging.error(f"Error logging IP and ports for {ip}: {e}")

COMMON_PORTS = [
    22, 21, 80, 8080, 3000, 5000, 6666, 443, 3389, 23, 25, 53, 110, 143, 445, 5900, 2375, 3306, 6379, 27017
]

def scan_ports(host, ports):
    try:
        nm = nmap.PortScanner()
        port_list = ','.join(map(str, ports))
        nm.scan(hosts=host, arguments=f'-p {port_list}')
        open_ports = []
        if 'tcp' in nm[host]:
            for port, port_info in nm[host]['tcp'].items():
                if port_info['state'] == 'open':
                    open_ports.append(port)
        return open_ports
    except Exception as e:
        logging.error(f"Error scanning {host}: {e}")
        return []

@click.command()
@click.option('--simulate', is_flag=True, default=False, help='Simulate the display (no hardware required)')
@click.option('--network', default='192.168.0.0/24', show_default=True, help='Network range to scan (default: 192.168.0.0/24)')
@click.option('--ports', default=','.join(map(str, COMMON_PORTS)), show_default=True, help='Comma-separated list of ports to scan (default: common ports)')
def main(simulate, network, ports):
    try:
        ports = list(map(int, ports.split(',')))
        
        online_hosts = get_online_hosts(network)
        remaining_hosts = len(online_hosts)
        backlog = deque(maxlen=5)

        epd = initialize_display(simulate=simulate)
        image = Image.new('1', (epd.width, epd.height), 0)

        if simulate:
            font_large = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 12)
            font_small = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 8)
        else:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 8)

        boot_text_styles = [
            {'text': 'Scanning...', 'position': (10, 10), 'font_size': 12}
        ]
        update_display(epd, image, boot_text_styles, full_refresh=True)
        time.sleep(2)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(scan_ports, host, ports): host for host in online_hosts}

            for future in concurrent.futures.as_completed(futures):
                host = futures[future]
                open_ports = future.result()
                remaining_hosts -= 1

                if open_ports:
                    log_ip_and_ports(host, open_ports)
                    backlog.appendleft((host, open_ports))

                text_styles = [
                    {'text': f"Scanning... {remaining_hosts} left", 'position': (10, 10), 'font_size': 10}
                ]

                y_position = 36
                for ip, ports in backlog:
                    text_styles.append({'text': f"IP: {ip}", 'position': (10, y_position), 'font_size': 10})
                    y_position += 16
                    text_styles.append({'text': f"Ports: {', '.join(map(str, ports))}", 'position': (10, y_position), 'font_size': 8})
                    y_position += 16

                update_display(epd, image, text_styles)
                time.sleep(2)

    except Exception as e:
        logging.error(f"Error in main process: {e}")
    finally:
        try:
            epd.sleep()
        except Exception as e:
            logging.error(f"Error shutting down the display: {e}")

if __name__ == "__main__":
    main()

