from lib7 import mqtt, menu_icons, hrv, history
from machine import Pin, I2C, ADC 
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
from filefifo import Filefifo
import framebuf, time, math, utime
from lib7 import hrv
from lib7 import menu_icons
from lib7 import buttons

class Screen:
    width: int = 128
    height: int = 64
    color: int = 1
    black: int = 0

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(Screen.width, Screen.height, i2c)
hrv_cl = hrv.HRV()
led = buttons.Led()
#timer = Timer(period=10, mode = Timer.PERIODIC, callback = lambda t: print(1))

def get_hr():
    HR_Raw = ADC(Pin(27, Pin.IN))
    return int( HR_Raw.read_u16() )

def menu(state: int):
    images = menu_icons.menu_Icons()    
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
    if sum(ppi_list) == 0:
        raise RuntimeError("Sum of ppi_list zero.")

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
    timer = Piotimer(freq=1000, callback=lambda t: setattr(timer, "count", timer.count+1))
    timer.count = 0
    detecting = False
    threshold = 35000
    current_max = 1
    current_max_interval = threshold
    ppi_list = []
    mean_bpm_list = []
    bpm = 0
    mean_bpm = 0
    mean_ppi = 0
    rm = 0
    sd = 0

    hr_buffer = Fifo(size=5)
    start_time = time.time()

    old_y = Screen.height // 2

    while not ReturnBtn.pressed:
        oled.fill(0)

        for x in range(Screen.width):

            if ReturnBtn.pressed:
                break

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
            print("THRESHOLD:", threshold)
            print(hr_datapoint)
            if hr_datapoint >= threshold:
                detecting = True
                if hr_datapoint > current_max:
                    current_max = hr_datapoint
                    current_max_interval = timer.count

            if hr_datapoint < threshold and detecting and timer.count > 300:
                detecting = False

                ppi_list.append(current_max_interval)
                current_max = threshold
                # print(ppi_list)
                # print("Timer: ", timer.count)
                timer.count = 0
                led.blink()

                if len(ppi_list) > 5:
                    ppi_list.pop(0)
                    if sum(ppi_list) != 0:
                        bpm = calculate_bpm(ppi_list)
                    else:
                        print("SUM OF PPI_LIST ZERO")
                    mean_bpm_list.append(bpm)

                    if len(mean_bpm_list) > 50:
                        mean_bpm_list.pop(0)
                print("bpm:", bpm)

            #Final report for hrv mode, values updated every 30 seconds.
            if time.time() - start_time >= 30 and mode == "hrv":
                now_time = utime.localtime(start_time)
                start_time = time.time()

                #NTP, MEAN PPI, MEAN HR, RMSSD, SDNN
                time_str = f"{now_time[0] % 100}/{now_time[1]:02d}/{now_time[2]:02d} {2 + now_time[3]:02d}:{now_time[4]:02d}"
                print(f"NTP: {time_str}")
                hrv_res = hrv_cl.calc_hrv(mean_bpm_list, ppi_list)
                    
                data = [f"{time_str}", f"AVG_BPM: {hrv_res[0]}", f"AVG_PPI: {hrv_res[1]}", f"RMSSD: {hrv_res[2]}", f"SDNN: {hrv_res[3]}"]

                if Mqtt.connected: #Data published to MQTT every 30 seconds
                    Mqtt.publish(f"{Mqtt.TOPIC_HRV}", f"{data}")
                history.store_Data(datalist=data)

            # draw stats 
            if mode == "hrv":
                # More stuff
                draw_stats(0, 0, {"BPM": bpm, "avgBPM": int(mean_bpm)})
                draw_stats(0, 54, {"RMSSD": rm, "SDNN": int(sd)})

            else:
                # BPM only
                draw_stats(0, 50, {"BPM": bpm})

            oled.show()
