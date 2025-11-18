from machine import Pin, I2C, ADC 
from ssd1306 import SSD1306_I2C
import framebuf, time
from piotimer import Piotimer

class Screen:
    width: int = 128
    height: int = 64
    color: int = 1
    black: int = 0

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(Screen.width, Screen.height, i2c)
#timer = Timer(period=10, mode = Timer.PERIODIC, callback = lambda t: print(1))


images = [
    bytearray([
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1b, 0xfd, 0x80, 0x3b, 
        0xfd, 0xc0, 0x3b, 0xfd, 0xc0, 0x3b, 0x9d, 0xc0, 0x3b, 0x9d, 0xc0, 0x3a, 0x05, 0xc0, 0x3a, 0x05, 
        0xc0, 0x3b, 0x9d, 0xc0, 0x3b, 0x9d, 0xc0, 0x3b, 0xfd, 0xc0, 0x3b, 0xfd, 0xc0, 0x1b, 0xfd, 0x80, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    bytearray([
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0x0f, 0x00, 0x1f, 0x9f, 0x80, 0x3f, 
        0xff, 0xc0, 0x3f, 0xff, 0xc0, 0x3e, 0x7f, 0xc0, 0x3c, 0x67, 0xc0, 0x18, 0x23, 0x80, 0x01, 0x08, 
        0x00, 0x0f, 0x9f, 0x00, 0x0f, 0x9f, 0x00, 0x07, 0xfe, 0x00, 0x03, 0xfc, 0x00, 0x01, 0xf8, 0x00, 
        0x00, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),      
    bytearray([
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0xff, 0x80, 0x1f, 0xff, 0x80, 0x1f, 0xff, 0x80, 0x1f, 
        0x9f, 0x80, 0x1f, 0x9f, 0x80, 0x1e, 0x07, 0x80, 0x1e, 0x07, 0x80, 0x1f, 0x9f, 0x80, 0x1f, 0x9f, 
        0x80, 0x1f, 0xff, 0x80, 0x1f, 0xff, 0x80, 0x1f, 0xff, 0x80, 0x18, 0x03, 0x00, 0x18, 0x03, 0x00, 
        0x1f, 0xff, 0x80, 0x07, 0xff, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
]

def get_hr(interval: float = 0):
    HR_Raw = ADC(Pin(27, Pin.IN))
    time.sleep(interval)
    return int( HR_Raw.read_u16() )

def menu(state: int):
    
    step_size = 21
    titles = (
            ["Live Pulse", "Display"],
            ["Title 2", "Title 2 Row 2", "Row 3"],
            "Title 3"
            )
    icon_y = 40
    
    cursor_x = int(step_size / 2 + state * step_size - 4)
    cursor_y = icon_y + 20
    
    title_x = 0
    title_y = 5

    oled.fill(0)
    for i in range(len(images)):
            img = framebuf.FrameBuffer(images[i], 20, 20, framebuf.MONO_HLSB)
            oled.blit(img, (step_size * i), icon_y)

    oled.text("^", cursor_x, cursor_y)
    if type(titles[state]) == list:
        for title in titles[state]:
            oled.text(title, title_x, title_y)
            title_y += 10
    else:
        oled.text(titles[state], title_x, title_y)

    oled.show()

def hr_monitor(ReturnBtn, graph: bool = False):
    """
    time_interval: int = 0
    timer = Piotimer(freq=100, callback=) TODO: increment interval
    detecting = False
    current_max = 0
    last_peak_time = 0
    THRESHOLD = 65536 / 2
    """

    old_y = Screen.height // 2
    while not ReturnBtn.pressed:
        oled.fill(0)
        for x in range(Screen.width):
            hr_datapoint = get_hr(0)
            if graph:
                y = int( Screen.height - (hr_datapoint / 65536 * Screen.height ) )
                if y > old_y:
                    for i in range(y - old_y):
                        oled.pixel(x, old_y+i, Screen.color)
                elif y < old_y:
                    for i in range(abs(old_y) - abs(y)):
                        oled.pixel(x, old_y-i, Screen.color)
                else:
                    oled.pixel(x, y, Screen.color)

                old_y = y
                oled.show()

            if ReturnBtn.pressed:
                break


"""
            # PPI Measuring
            # TODO: FIX TIMERS
            if hr_datapoint > THRESHOLD:
                deteting = True
                if hr_datapoint > current_max:
                    current_max = hr_datapoint

            else:
                if detecting:
                    detecting = False
                    time_interval = 0
"""


    #final report

