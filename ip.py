import os
import time
import subprocess
from PIL import Image, ImageDraw, ImageFont
import click
from simulate_eink import SimulatedEPD

def initialize_display(simulate=True):
    if simulate:
        return SimulatedEPD()
    else:
        from waveshare_epd import epd2in13_V4
        epd = epd2in13_V4.EPD()
        epd.init()
        return epd

def update_display(epd, image, text_styles, logo_path=None):
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, epd.width, epd.height), fill=0)
    
    if logo_path:
        logo = Image.open(logo_path)
        logo_width, logo_height = logo.size
        if logo_width > epd.width or logo_height > epd.height:
            logo.thumbnail((epd.width, epd.height))
        center_x = (epd.width - logo.width) // 2
        center_y = (epd.height - logo.height) // 2
        image.paste(logo, (center_x, center_y))
    
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
            font = ImageFont.load_default()
        draw.text(position, text, font=font, fill=255)
    
    epd.display(epd.getbuffer(image))

def get_ip_address(simulate=True):
    if simulate:
        return "192.168.1.100"
    else:
        while True:
            result = subprocess.run(['ip', 'addr', 'show', 'wlan0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ip_address = next((line.split()[1].split('/')[0] for line in result.stdout.decode().splitlines() if 'inet ' in line), None)
            if ip_address:
                return ip_address
            time.sleep(1)

@click.command()
@click.option('--simulate', is_flag=True, default=False, help='Simulate the display (no hardware required)')
def main(simulate):
    ip_address = None
    script_dir = os.path.dirname(__file__)
    
    logo_path = os.path.join(script_dir, "logo.png")
    
    epd = initialize_display(simulate=simulate)
    image = Image.new('1', (epd.width, epd.height), 0)
    
    boot_text_styles = [{'text': 'Waiting for IP...', 'position': (10, epd.height - 20), 'font_size': 9}]
    
    while not ip_address:
        ip_address = get_ip_address(simulate=simulate)
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
