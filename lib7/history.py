import time
from machine import I2C, Pin
from ssd1306 import SSD1306_I2C
from buttons import Encoder

class Screen:
    width: int = 128
    height: int = 64
    color: int = 1
    black: int = 0

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(Screen.width, Screen.height, i2c)

def update_Display(records: dict, counter: int):
    oled.fill(0)   
    oled.text("[History]", 28, 0,  1)
    oled.text("<", 0, 32)
    oled.text(">", 120, 32)
    oled.show()

    values = records[f"Patient[{counter}]"]
    
    for i in range(len(values)):
        time.sleep(0.25)
        oled.text(values[i], 28, 20 +(8*i))
        oled.show()

def get_Med_History(ReturnBtn: object, mode: str):
    records = {}
    counter = 1

    oled.fill(0)
    oled.show()

    files = Filefifo(5, name = "history_files.txt")

    # !THE INPUT DATA FOR THE DICTIONARY MUST BE A LIST OF VALUES!
    for i in range(5):
        if files.has_data():
            record = files.get()
            records.update({f"Patient[{i+1}]" : record})

    #First Record Displayed:
    update_Display(records, 1)

    while not ReturnBtn.pressed:
        rot = Encoder(10, 11, 12)

        if rot.fifo.has_data():
            rotator = rot.fifo.get()

            if rotator == 1 and 1 <= counter < 5:
                counter += 1
                update_Display(records, counter)   
                
            elif rotator == -1 and 1 < counter <= 5:
                counter -= 1
                update_Display(records, counter)

        if ReturnBtn.pressed:
            break


    