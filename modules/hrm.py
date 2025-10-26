from machine import Pin, ADC
import time

HR_Raw = ADC(Pin(27, Pin.IN))
Powered = Pin("LED", Pin.OUT)
threshold_max = 600
threshold_min = 500
time_mills = 5000
beat = 0
start_time = time.time()

def getHRM():
        Powered.on()
        time.sleep(0.5)
        Powered.off()
        time.sleep(0.5)
        
        return HR_Raw.read_u16()

def beat_Count(param1):
    
    return param1 - start_time


def convert_HR():
    while True:
        raw_Data = getHRM()
        value = raw_Data >> 6
        present = time.time()
        
        if beat_Count(present) > time_mills:
            bpm = beat * 12
            print(bpm)
            beat = 0
            start_time = present
            time.sleep(0.5)
        

        
if __name__ == "__main__":
    convert_HR()

