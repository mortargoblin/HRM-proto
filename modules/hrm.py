from machine import Pin, ADC
import time

HR_Raw = ADC(Pin(27, Pin.IN))
Powered = Pin("LED", Pin.OUT)
threshold_max = 600
threshold_min = 500
time_mills = 5000
beat = 0
start_time = time.time()
prev_value = threshold_min

def getHRM():
        Powered.on()
        time.sleep(0.5)
        Powered.off()
        time.sleep(0.5)
        return HR_Raw.read_u16()

def convert_HR():
    global beat, start_time, prev_value
    while True:
        raw_Data = getHRM()
        value = raw_Data >> 6
        present = time.time()

        if (prev_value < threshold_min) and (value > threshold_max):
            beat += 1
        prev_value = value

        if (present - start_time) * 1000 > time_mills:
            bpm = int(beat * (60000 / time_mills))
            print(bpm)
            beat = 0
            start_time = present
            time.sleep(0.5)
        
if __name__ == "__main__":
    convert_HR()

