from PIL import Image

class SimulatedEPD:
    def __init__(self):
        self.width = 122
        self.height = 250
        self.image = Image.new('1', (self.width, self.height), 255)

    def init(self):
        print("Simulated EPD initialized.")

    def getbuffer(self, image):
        return image

    def display(self, image):
        print("Full refresh triggered.")
        self._simulate_display(image)

    def displayPartial(self, image):
        print("Partial refresh triggered.")
        self._simulate_display(image)

    def _simulate_display(self, image):
        image.save("./output/epd_image.png")
        print("Image saved as epd_image.png")

    def sleep(self):
        print("Simulated EPD entering sleep mode.")
