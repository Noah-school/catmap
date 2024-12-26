import os
import time
import subprocess
from PIL import Image
import click
from display import initialize_display, update_display
from config import Config
import ipaddress


class Interface:
    def __init__(self, ip, mask, desc):
        ipa = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
        self.network = ipa.with_prefixlen
        self.ip = ipa.network_address
        self.prefix = ipa.prefixlen
        self.desc = desc
        
    def __str__(self):
        return self.network
    
    def __format__(self, format_spec):
        return str(self).__format__(format_spec)

config_path = os.path.join(os.path.dirname(__file__), 'catmap.conf')
config = Config(config_path)

def get_ipaddress_win():
    result = subprocess.run(['ipconfig', '/all' ,'|', 'findstr', 'Description IPv4 Subnet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    ipInfo = []
    lines = result.stdout.decode().splitlines()
    ip_line = None
    subnet_line = None
    
    for line in lines:
        if "IPv4 Address" in line:
            ip = line.split(':')[1].strip()
            ip_line = ip.split('(')[0].strip()
        elif "Subnet Mask" in line:
            subnet_line = line.split(':')[1].strip()
        elif "Description" in line:
            if ip_line and subnet_line:
                desc_line = line.split(':')[1].strip()
                network = Interface(ip_line, subnet_line, desc_line)
                ipInfo.append(network)
                ip_line = None
                subnet_line = None
    return ipInfo

def get_ip_address(simulate=True, redo_config=False):
    if simulate:
        config_data = config.get()
        ipInfo = get_ipaddress_win()
        
        if len(ipInfo) == 1:
            config_data['network'] = ipInfo[0].ip
            return ipInfo[0]
        
        if 'network' in config_data and not redo_config:
            return config_data['network']
            
        else:
            click.echo("Multiple IP's found:")
            for i, network in enumerate(ipInfo, 1):
                click.echo(f"{i}. {network.network}")
            
            choice = click.prompt("Set default network", type=click.IntRange(1, len(ipInfo)))
            selectedNetwork = ipInfo[choice - 1]
            
            changePrefix = click.confirm(f"Do you want to change the Prefix? (current: {selectedNetwork.prefix})", default=False)
            if changePrefix:
                newPrefix = click.prompt("Enter new Prefix", type=click.IntRange(0, 32))
                config_data['network'] = f"{selectedNetwork.ip}/{newPrefix}"
        config.config = config_data
        config.save()
        return config_data['network']
    else:
        while True:
            result = subprocess.run(['ip', 'addr', 'show', 'wlan0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ip_address = next((line.split()[1] for line in result.stdout.decode().splitlines() if 'inet ' in line), None)
            if ip_address:
                return ip_address
            time.sleep(1)

@click.command()
@click.option('--simulate', is_flag=True, default=False, help='Simulate the display (no hardware required)')
@click.option('--reset-config', is_flag=True, default=False, help='reset the default network configuration')
def main(simulate, reset_config):
    ip_address = None
    script_dir = os.path.dirname(__file__)
    
    logo_path = os.path.join(script_dir, "logo.png")
    
    epd = initialize_display(simulate=simulate)
    image = Image.new('1', (epd.width, epd.height), 0)
    
    boot_text_styles = [{'text': 'Waiting for IP...', 'position': (4 , epd.height - 20), 'font_size': 9}]
    
    while not ip_address:
        ip_address = get_ip_address(simulate, reset_config)
        boot_text_styles[0]['text'] = f"IP: {ip_address : ^22}" if ip_address else "Waiting for IP..."
        update_display(epd, image, boot_text_styles, logo_path=logo_path)
        time.sleep(1)
    
    if simulate:
        boot_text_styles[0]['text'] = f"IP: {ip_address : ^22}"
        update_display(epd, image, boot_text_styles, logo_path=logo_path)
        time.sleep(5) 
    
    epd.sleep()

if __name__ == "__main__":
    main()
