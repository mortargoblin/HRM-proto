from machine import Pin, ADC
import time

HR_Data = ADC(Pin(26, Pin.IN))
Powered = Pin("LED", Pin.OUT)

def getHRM():
    Powered.on()
    time.sleep(0.5)
    Powered.off()
    time.sleep(0.5)
    return HR_Data.read_u16()

