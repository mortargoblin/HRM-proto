from machine import Pin, ADC
import time

HR_Raw = ADC(Pin(27, Pin.IN))
Powered = Pin("LED", Pin.OUT)
HR_Real = 0

def getHRM():
    while True:
        Powered.on()
        time.sleep(0.5)
        Powered.off()
        value = HR_Raw.read_u16()
        HR_Real = HR_Raw.read_u16() / 4096 * 3.3
        time.sleep(0.5)
        print(f"HR: {value}")

getHRM()

