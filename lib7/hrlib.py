from machine import Pin, I2C, ADC 
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
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

    return 60000 / (sum(ppi_list[-5:]) / 5)

def hr_monitor(ReturnBtn, mode: str):
    timer = Piotimer(freq=1000, callback=lambda t: setattr(t, "count", t.count+1))
    timer.count = 0
    detecting = False
    current_max = 1
    threshold = 65536 / 2 + 1600
    ppi_list = []
    mean_bpm_list = []
    bpm = 0

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

            if mode == "hr":
                # BPM only
                _x = Screen.width // 2
                _y = Screen.height // 2 + 20
                _width = 30
                _height = 13
                oled.fill_rect(
                        _x - _width // 2,
                        _y - _height // 2,
                        _width, _height, Screen.color)
                oled.text(
                        str(int(bpm)),
                        _x - 12,
                        _y - 4,
                        Screen.black)


            elif mode == "hrv":
                # More stuff
                pass
            

            old_y = y
            oled.show()

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

                            if len(mean_bpm_list) > 5:
                                mean_bpm_list.pop(0)
                        print("bpm:", bpm)

            if ReturnBtn.pressed:
                break

            #Final report for hrv mode
            if time.time() - start_time >= 30 and mode == "hrv":
                start_time = time.time()
                
                #MEAN PPI, MEAN HR, RMSSD, SDNN
                mean_ppi = sum(ppi_list) / len(ppi_list)
                mean_bpm = sum(mean_bpm_list) / len(mean_bpm_list)
                sd = hrv.sdnn(ppi_list)
                rm = hrv.rmssd(mean_bpm_list)
                
                print("[AVG_PPI]: ", mean_ppi, "ms")
                print("[AVG_BPM]: ", mean_bpm, "/s")
                print("[SDNN]: ", sd, "ms")
                print("[RMSSD]: ", rm, "ms")
