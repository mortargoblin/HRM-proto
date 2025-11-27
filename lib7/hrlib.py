from lib7 import mqtt
from machine import Pin, I2C, ADC 
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
from filefifo import Filefifo
import framebuf, time, math
from lib7 import hrv

class Screen:
    width: int = 128
    height: int = 64
    color: int = 1
    black: int = 0

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(Screen.width, Screen.height, i2c)
#timer = Timer(period=10, mode = Timer.PERIODIC, callback = lambda t: print(1))


images = [
    bytearray([ #Heart Rate Mode image
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0x0f, 0x00, 0x1f, 0x9f, 0x80, 0x3f, 
        0xff, 0xc0, 0x3f, 0xff, 0xc0, 0x3e, 0x7f, 0xc0, 0x3c, 0x67, 0xc0, 0x18, 0x23, 0x80, 0x01, 0x08, 
        0x00, 0x0f, 0x9f, 0x00, 0x0f, 0x9f, 0x00, 0x07, 0xfe, 0x00, 0x03, 0xfc, 0x00, 0x01, 0xf8, 0x00, 
        0x00, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  
    bytearray([ # Advanced mode image
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1b, 0xfd, 0x80, 0x3b, 
        0xfd, 0xc0, 0x3b, 0xfd, 0xc0, 0x3b, 0x9d, 0xc0, 0x3b, 0x9d, 0xc0, 0x3a, 0x05, 0xc0, 0x3a, 0x05, 
        0xc0, 0x3b, 0x9d, 0xc0, 0x3b, 0x9d, 0xc0, 0x3b, 0xfd, 0xc0, 0x3b, 0xfd, 0xc0, 0x1b, 0xfd, 0x80, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    bytearray([ #Kubios Analysis Image
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xf8, 0x00, 0x07, 0xfe, 0x00, 0x0f, 0x0f, 0x00, 0x0f, 
        0xff, 0x00, 0x0f, 0xff, 0x00, 0x0f, 0xff, 0x00, 0x0f, 0xff, 0x00, 0x0f, 0x9f, 0x00, 0x0f, 0x0f, 
        0x00, 0x0f, 0x0f, 0x00, 0x0f, 0x9f, 0x00, 0x0f, 0xff, 0x00, 0x0f, 0x0f, 0x00, 0x0e, 0x07, 0x00, 
        0x0f, 0xff, 0x00, 0x07, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    bytearray([ #History image
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0xff, 0x80, 0x1f, 0xff, 0x80, 0x1f, 0xff, 0x80, 0x1f, 
        0x9f, 0x80, 0x1f, 0x9f, 0x80, 0x1e, 0x07, 0x80, 0x1e, 0x07, 0x80, 0x1f, 0x9f, 0x80, 0x1f, 0x9f, 
        0x80, 0x1f, 0xff, 0x80, 0x1f, 0xff, 0x80, 0x1f, 0xff, 0x80, 0x18, 0x03, 0x00, 0x18, 0x03, 0x00, 
        0x1f, 0xff, 0x80, 0x07, 0xff, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),   
]

def get_hr():
    HR_Raw = ADC(Pin(27, Pin.IN))
    return int( HR_Raw.read_u16() )

def menu(state: int):
    
    step_size = 21
    titles = (
            ["[HRM]", "Heart Rate"],
            ["[HRV]", "Measurements"],
            ["[Kubios]", "Cloud Services"],
            ["[Files]", "Medical History"]
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

def calculate_bpm(ppi_list: list[int]):
    if len(ppi_list) < 5:
        raise RuntimeError("List too short")

    return int(60000 / (sum(ppi_list[-5:]) / 5))

def draw_stats(x: int, y:int, stats):

    font_width = 8
    width = 0
    height = 10

    for key, value in stats.items():
        width += len(key) * font_width + 30

    oled.fill_rect(
            x,
            y,
            width,
            height,
            Screen.color
            )

    offset = 0
    for key, value in stats.items():
        oled.text(
                str(key),
                x + offset,
                y + 1,
                Screen.black
                )
        oled.text(
                str(value),
                x + offset + len(key) * font_width + 3,
                y + 1,
                Screen.black
                )
        offset += len(key) * font_width + 30

def hr_monitor(ReturnBtn, mode: str, Mqtt):
    timer = Piotimer(freq=1000, callback=lambda t: setattr(t, "count", t.count+1))
    timer.count = 0
    detecting = False
    current_max = 1
    threshold = 65536 / 2 + 1600
    ppi_list = []
    mean_bpm_list = []
    bpm = 0
    mean_bpm = 0
    mean_ppi = 0

    hr_buffer = Fifo(size=5)
    start_time = time.time()

    old_y = Screen.height // 2

    while not ReturnBtn.pressed:
        oled.fill(0)

        for x in range(Screen.width):
            hr_buffer.put(get_hr())
            hr_datapoint = hr_buffer.get()
            # print(hr_datapoint)
            
            ### Drawing ###
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

            ### PPI Measuring ###
            if hr_datapoint > threshold:
                detecting = True
                # if hr_datapoint > current_max:
                #    current_max = hr_datapoint

            else:
                if detecting:
                    detecting = False
                    if timer.count > 1500:
                        timer.count = 0
                    if timer.count > 250:
                        ppi_list.append(timer.count)
                        timer.count = 0
                        if len(ppi_list) > 5:
                            ppi_list.pop(0)
                            bpm = calculate_bpm(ppi_list)
                            mean_bpm_list.append(bpm)

                            if len(mean_bpm_list) > 50:
                                mean_bpm_list.pop(0)
                        print("bpm:", bpm)

            if ReturnBtn.pressed:
                break

            #Final report for hrv mode, values updated every 30 seconds.
            # report for hrv mode
            if time.time() - start_time >= 30 and mode == "hrv":
                start_time = time.time()
                
                #MEAN PPI, MEAN HR, RMSSD, SDNN
                mean_ppi = sum(ppi_list) / len(ppi_list)
                mean_bpm = sum(mean_bpm_list) / len(mean_bpm_list)
                sd = hrv.sdnn(ppi_list)
                rm = hrv.rmssd(mean_bpm_list)
                
                #Data published to MQTT every 30 seconds:
                data: list[str, float | int] = [
                        f"AVG_BPM: {mean_bpm}", 
                        f"AVG_PPI: {mean_ppi}", 
                        f"RMSSD: {rm}", 
                        f"SDNN: {sd}"
                ]

                Mqtt.publish(f"{Mqtt.TOPIC_HRV}", f"{data}")

            # draw stats 
            if mode == "hrv":
                # More stuff
                draw_stats(0, 50, {"BPM": bpm, "AVG_PPI": int(mean_ppi)})
                
            else:
                # BPM only
                draw_stats(0, 50, {"BPM": bpm})

            oled.show()

#History functions:
def update_Display(records: dict, counter: int):
    oled.fill(0)   
    oled.text("[History]", 0, 0,  1)
    oled.text(f"[P-{counter}]", 90, 0, 1)
    oled.text("<", 0, 32)
    oled.text(">", 120, 32)
    oled.show()

    values = records[f"Patient[{counter}]"]
    
    for i in range(len(values)):
        time.sleep(0.25)
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

    with open('patient_records.txt', 'r+') as file:
        linecount: int = len(file.readlines())
        file.seek(0)
            
        if linecount > 0:
            for line in file:
                line = line.strip()
                updated_records.append(line)
            if linecount >= 5:    
                updated_records.pop(0)
        updated_records.append(datalist)
        
    try:
        with open('patient_records.txt', 'w') as file:
            file.write(f'\n'.join(map(str, updated_records)))
            file.seek(0)
            print(file.read())
            
    except Exception as e:
        print(f'Error storing data: {e}')
        
