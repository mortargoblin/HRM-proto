import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

class Screen:
    width: int = 128
    height: int = 64
    color: int = 1
    black: int = 0

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(Screen.width, Screen.height, i2c)

#History functions:
def update_Display(records: dict, counter: int):
    oled.fill(0)   
    oled.text("[History]", 0, 0,  1)
    oled.text(f"[P-{counter}]", 90, 0, 1)
    
    if counter == 1:
        oled.text(">", 120, 32)
    elif counter in [2, 3, 4]:
        oled.text("<", 0, 32)
        oled.text(">", 120, 32)
    else:
        oled.text("<", 0, 32)
    oled.show()

    values = records[f"Patient[{counter}]"]
    
    for i in range(len(values)):
        time.sleep(0.05)
        value = values[i].strip("'")
        oled.text(value, 14, 20 +(8*i))
        oled.show()

def get_Med_History(ReturnBtn: object, Encoder):
    records = {}
    counter = 1

    oled.fill(0)
    oled.show()
    try: 
        with open('patient_records.txt', 'r') as file:
            lines = 0
            for line in file:
                line = line.strip()
                line = line[1:-1]
                record = line.split(", ")
                records.update({f"Patient[{lines+1}]" : record})          
                lines += 1

    except Exception as e:
        print(f'Error: {e}')
    
    #First Record Displayed:
    update_Display(records, 1)

    while not ReturnBtn.pressed:

        if Encoder.fifo.has_data():
            rotator = Encoder.fifo.get()

            if rotator == 1 and 1 <= counter < 5:
                counter += 1
                update_Display(records, counter)   
                
            elif rotator == -1 and 1 < counter <= 5:
                counter -= 1
                update_Display(records, counter)

        if ReturnBtn.pressed:
            break

#Storing data into the patient_records.txt file.
def store_Data(datalist):
    updated_records = []
    updated_records.append(datalist)

    with open('patient_records.txt', 'r+') as file:
        linecount: int = len(file.readlines())
        file.seek(0)
            
        if linecount > 0:
            for line in file:
                line = line.strip()
                updated_records.append(line)
            if linecount >= 5:    
                updated_records.pop()
        
    try:
        with open('patient_records.txt', 'w') as file:
            file.write(f'\n'.join(map(str, updated_records)))
            file.seek(0)
            print(file.read())
            
    except Exception as e:
        print(f'Error storing data: {e}')