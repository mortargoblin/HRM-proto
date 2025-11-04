import time
from machine import UART, Pin, ADC, I2C
from ssd1306 import SSD1306_I2C

HR_Raw = ADC(Pin(27, Pin.IN))

def get_hr(interval: float = 0.05):
    time.sleep(interval)
    return int( HR_Raw.read_u16() )

class Screen:
    width: int = 128
    height: int = 64
    color: int = 1
    black: int = 0

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(Screen.width, Screen.height, i2c)

print(Screen.width)

def display_pulse():
    while True:
        oled.fill(0)
        old_y = 1
        for x in range(Screen.width):
            y = int( get_hr(0) / 65536 * Screen.height )
            if y > old_y:
                for i in range(y - old_y):
                    oled.pixel(x, old_y+i, Screen.color)
            elif y < old_y:
                for i in range(abs(old_y) - abs(y)):
                    oled.pixel(x, old_y-i, Screen.color)
            else:
                oled.pixel(x, y, Screen.color)

            old_y = y
            print(y)
            oled.show()

display_pulse()

