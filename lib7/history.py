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

#-------------------------------------------------#
# Displays patient_records.txt data on the screen #
#-------------------------------------------------#
def update_Display(records: dict, counter: int):
    oled.fill(0)   
    oled.text("[History]", 0, 0,  1)
    oled.text(f"   P-{counter}", 70, 0, 1)

    max_index = len(records)
    
    if max_index > 1:
        if counter == 1:
            oled.text(">", 120, 32)
        elif counter == max_index:
            oled.text("<", 0, 32)
        else:
            oled.text("<", 0, 32)
            oled.text(">", 120, 32)
    oled.show()

    # A list of data consisting of BPM, PPI, RMSSD, SDNN.
    values = records[f"Patient[{counter}]"]
    
    for i in range(len(values)):
        time.sleep(0.05)
        value = values[i].strip("'")
        # limit text length to screen width (16 chars max with default font)
        oled.text(value[:16], 14, 20 +(8*i))
        oled.show()

#------------------------------------------------------------#
# Function to convert text file data to be displayed in oled #
#------------------------------------------------------------#
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
                if not line:
                    continue
                line = line[1:-1]
                record = line.split(", ")
                records.update({f"Patient[{lines+1}]" : record})          
                lines += 1

    except Exception as e:
        print(f'Error: {e}')
    
    if not records:
        oled.fill(0)
        oled.text("[History]", 0, 0, 1)
        oled.text("No records yet", 0, 20, 1)
        oled.show()
        time.sleep(2)
        return
    
    max_index = len(records)

    #First record displayed:
    update_Display(records, counter)

    while not ReturnBtn.pressed:
        if Encoder.fifo.has_data():
            rotator = Encoder.fifo.get()

            if rotator == 1 and counter < max_index:
                counter += 1
                update_Display(records, counter)   
                
            elif rotator == -1 and counter > 1:
                counter -= 1
                update_Display(records, counter)

        if ReturnBtn.pressed:
            break

#-------------------------------------------#
# Function to store data into the .txt file #
#-------------------------------------------#
def store_Data(datalist):
    updated_records = []
    updated_records.append(datalist) #New data to be saved first before pushing out the oldest data off of the patient_records.txt file 

    with open('patient_records.txt', 'r+') as file:
        linecount: int = len(file.readlines())
        file.seek(0)
            
        if linecount > 0:
            for line in file:
                line = line.strip()
                updated_records.append(line)
            if linecount >= 5: #The number controls the maximum amount of lines that can be stored inside the file patient_records.txt    
                updated_records.pop()
        
    try:
        with open('patient_records.txt', 'w') as file:
            file.write(f'\n'.join(map(str, updated_records))) #Finally stores the new array of data inside the file, whilst first converting all nested arrays to strings and separating each with a lineswitch
            file.seek(0)
            
    except Exception as e:
        print(f'Error storing data: {e}')