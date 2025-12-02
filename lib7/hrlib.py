from lib7 import mqtt
from machine import Pin, I2C, ADC 
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
from filefifo import Filefifo
import framebuf, time, math
from lib7 import hrv
from lib7 import menu_icons

class Constants:
    #Screen
    SCREEN_WIDTH = 128
    SCREEN_HEIGHT = 64
    
    #HR measurement
    ADC_MAX = 65536
    THRESHOLD_BASE = ADC_MAX / 2
    THRESHOLD_OFFSET = 1600
    THRESHOLD = THRESHOLD_BASE + THRESHOLD_OFFSET
    
    #Timing
    MIN_PPI = 250 #ms
    MAX_PPI = 1500 #ms
    HRV_INTERVAL = 30 #s
    PPI_WINDOW_SIZE = 5
    BPM_WINDOW_SIZE = 50
    
    #display
    MENU_ICON_SIZE = 20
    MENU_ICON_SPACING = 21
    MENU_ICON_Y = 40
    STATS_HEIGHT = 10
    FONT_WIDTH = 8
    
class Screen:
    width: int = Constants.SCREEN_WIDTH
    height: int = Constants.SCREEN_HEIGHT
    color: int = 1
    black: int = 0

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(Screen.width, Screen.height, i2c)
#timer = Timer(period=10, mode = Timer.PERIODIC, callback = lambda t: print(1))

def get_hr():
    HR_Raw = ADC(Pin(27, Pin.IN))
    return int( HR_Raw.read_u16() )

def menu(state: int, show_animation=True):
    images = menu_icons.menu_Icons()    
    titles = (
        ["[HRM]", "Heart Rate"],
        ["[HRV]", "Measurements"],
        ["[Kubios]", "Cloud Services"],
        ["[Files]", "Medical History"]
    )
    
    oled.fill(0)
    
    #box around icon
    for i in range(len(images)):
        img = framebuf.FrameBuffer(images[i], 20, 20, framebuf.MONO_HLSB)
        if i == state:
            oled.rect(Constants.MENU_ICON_SPACING * i - 1, 
                     Constants.MENU_ICON_Y - 1, 
                     22, 22, 1)
        oled.blit(img, (Constants.MENU_ICON_SPACING * i), Constants.MENU_ICON_Y)
    
    title_x = 0
    title_y = 5
    
    if type(titles[state]) == list:
        for j, title in enumerate(titles[state]):
            oled.text(title, title_x, title_y + j*10)
    else:
        oled.text(titles[state], title_x, title_y)
    
    arrow_x = int(Constants.MENU_ICON_SPACING / 2 + state * Constants.MENU_ICON_SPACING - 4)
    arrow_y = Constants.MENU_ICON_Y + 20
    oled.text("^", arrow_x, arrow_y)
    
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
        
def hr_monitor(ReturnBtn, mode, Mqtt):
    finger_on = False
    bpm = 0
    
    hr_fifo = Fifo(size=5)
    hrv_time = time.time()
    measure_start = None
    last_y = Screen.height // 2
    
    # Beat detection
    beat_times = []
    last_beat_time = 0
    
    oled.fill(0)
    oled.text("Place finger", 30, 30)
    oled.show()
    time.sleep(1)
    
    ReturnBtn.pressed = False

    while True:
        if ReturnBtn.pressed:
            ReturnBtn.pressed = False
            return
        
        oled.fill(0)
        oled.text("Live Signal", 40, 0)
        
        signal_min = 65535
        signal_values = []
        
        for x in range(Screen.width):
            if ReturnBtn.pressed:
                ReturnBtn.pressed = False
                return
            
            hr_fifo.put(get_hr())
            hr_val = hr_fifo.get()
            signal_values.append(hr_val)
            
            if hr_val < signal_min:
                signal_min = hr_val

            inverted_val = 65535 - hr_val
            y = int(Screen.height - (inverted_val / 65536 * Screen.height))
            
            if y > last_y:
                for i in range(y - last_y):
                    oled.pixel(x, last_y + i, 1)
            elif y < last_y:
                for i in range(last_y - y):
                    oled.pixel(x, last_y - i, 1)
            else:
                oled.pixel(x, y, 1)
            
            last_y = y
        
        #average
        avg_signal = sum(signal_values) / len(signal_values)
        
        if avg_signal < 1000:
            if not finger_on:
                finger_on = True
                measure_start = time.time()
                beat_times = []
                last_beat_time = 0
                oled.fill(0)
                oled.text("Measuring", 35, 30)
                oled.show()
                time.sleep(0.5)
        else:
            finger_on = False
            bpm = 0
            measure_start = None
        
        if finger_on:
            current_time = time.ticks_ms()
            
            # Detect heartbeat when signal drops below threshold
            if signal_min < 280:
                if last_beat_time == 0:
                    last_beat_time = current_time
                else:
                    # calculate time between heartbeats
                    time_diff = time.ticks_diff(current_time, last_beat_time)
                    
                    if 250 < time_diff < 1500:
                        beat_times.append(time_diff)
                        last_beat_time = current_time
                        
                        #keep only last 5 beats
                        if len(beat_times) > 5:
                            beat_times.pop(0)
                        
                        # Calculate bpm
                        if len(beat_times) > 0:
                            avg_beat = sum(beat_times) / len(beat_times)
                            bpm = int(60000 / avg_beat)
            
            # reset if too long since last beat
            if last_beat_time > 0:
                time_since_beat = time.ticks_diff(current_time, last_beat_time)
                if time_since_beat > 2000:
                    beat_times = []
                    last_beat_time = 0
                    bpm = 0
        
        #Final report for hrv mode, values updated every 30 seconds.
        if mode == "hrv" and finger_on and time.time() - hrv_time >= 30:
            if len(beat_times) > 1:
                avg_ppi = sum(beat_times) / len(beat_times)
                avg_bpm = int(60000 / avg_ppi) if avg_ppi > 0 else 0
                
                sd_val = hrv.sdnn(beat_times)
                rm_val = hrv.rmssd(beat_times)
                
                now_time = time.localtime()
                time_str = f"{now_time[2]:02d}/{now_time[1]:02d}"
                
                data = [
                    time_str,
                    f"AVG_BPM: {avg_bpm}", 
                    f"AVG_PPI: {int(avg_ppi)}", 
                    f"RMSSD: {rm_val:.1f}", 
                    f"SDNN: {sd_val:.1f}"
                ]
                
                try:
                    from lib7 import history
                    history.store_Data(data)
                except:
                    pass
                
                try:
                    Mqtt.publish(f"{Mqtt.TOPIC_HRV}", str(data))
                except:
                    pass
            
            hrv_time = time.time()
        
        #display
        if not finger_on:
            oled.text("No finger", 40, 30)
            bpm = 0
        else:
            if measure_start:
                elapsed = int(time.time() - measure_start)
                oled.text(f"Time: {elapsed}s", 40, 55)
        
        #show BPM
        if finger_on and bpm > 0:
            draw_stats(20, 40, {"BPM": bpm})
        else:
            draw_stats(20, 40, {"BPM": 0})
        
        oled.show()
