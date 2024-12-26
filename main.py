import os
import time
import nmap
import json
import click
import logging
import concurrent.futures
from PIL import Image
from collections import deque
from display import initialize_display, update_display
from config import Config

config_path = os.path.join(os.path.dirname(__file__), 'catmap.conf')
config = Config(config_path)
config_data = config.get()
currentIP = config_data.get('network')

logging.basicConfig(filename='./output/errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_online_hosts(network):
    try:
        nm = nmap.PortScanner()
        logging.info(f"Scanning network: {network}")
        nm.scan(hosts=network, arguments='-sn --unprivileged')
        logging.info(f"Scan results: {nm.all_hosts()}")
        online_hosts = [host for host in nm.all_hosts() if nm[host].state() == "up"]
        return online_hosts
    except Exception as e:
        logging.error(f"Error getting online hosts: {e}")
        return []

def log_open(ip, open_ports):
    data = {
        "host": ip,
        "ports": open_ports
    }
    with open('./output/online_ips_ports.json', 'r+') as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
        existing_data.append(data)
        f.seek(0)
        json.dump(existing_data, f, indent=4)
        f.truncate()

def log_closed(ip):
    with open('./output/closed_ip.txt', 'a') as f:
        f.write(f"{ip}\n")

def get_ports():
    ports = config_data.get('ports', '')
    return list(map(int, ports.split(','))) if ports else []

default_ports = get_ports()

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
@click.option('--network', default=f'{currentIP}', show_default=True, help='Network range to scan')
@click.option('--ports', default=','.join(map(str, default_ports)), show_default=True, help='Comma-separated list of ports to scan')
def main(simulate, network, ports):
    try:
        ports = list(map(int, ports.split(',')))
        online_hosts = get_online_hosts(network)
        remaining_hosts = len(online_hosts)
        backlog = deque(maxlen=5)

        epd = initialize_display(simulate=simulate)
        image = Image.new('1', (epd.width, epd.height), 0)
        
        boot_text_styles = [
            {'text': 'Scanning...', 'position': (4, 10), 'font_size': 12}
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
                    log_open(host, open_ports)
                    backlog.appendleft((host, open_ports))
                else:
                    print(f"No open ports found for {host}")
                    log_closed(host)
                
                text_styles = [
                    {'text': f"Scanning... {remaining_hosts} left", 'position': (4, 10), 'font_size': 10}
                ]

                y_position = 36
                for ip, ports in backlog:
                    text_styles.append({'text': f"IP: {ip}", 'position': (4, y_position), 'font_size': 10})
                    y_position += 16
                    text_styles.append({'text': f"Ports: {', '.join(map(str, ports))}", 'position': (4, y_position), 'font_size': 8})
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
