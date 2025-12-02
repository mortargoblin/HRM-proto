from machine import Pin
from fifo import Fifo
import utime

class Encoder:
    pressed: bool = False
    def __init__(self, rot_a, rot_b, rot_btn=None):
        self.a = Pin(rot_a, mode=Pin.IN, pull=Pin.PULL_UP)
        self.b = Pin(rot_b, mode=Pin.IN, pull=Pin.PULL_UP)
        self.fifo = Fifo(30, typecode='i')
        self.a.irq(handler=self.handler, trigger=Pin.IRQ_RISING, hard=True)

        if rot_btn != None:
            self.btn = Pin(rot_btn, mode=Pin.IN, pull=Pin.PULL_UP)
            self.btn.irq(handler=self.button_handler, trigger=Pin.IRQ_FALLING)

    def handler(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

    def button_handler(self, pin):
        utime.sleep_ms(20)
        if not pin.value():
            self.pressed = True

class Return:
    #return button, used for returning
    pressed: bool = False

    def __init__(self, pin, mode, pull):
        self.btn = Pin(pin, mode = mode, pull = pull)
        self.btn.irq(handler=self.handler, trigger=self.btn.IRQ_FALLING, hard = True)

    def handler(self, pin):
        self.pressed = True

# sw_0 = Pin(9, mode = Pin.IN, pull = Pin.PULL_UP)

class Led:
    def __init__(self):
        self.led = Pin("LED")

    def blink(self):
        self.led.on()
        self.led.off()
