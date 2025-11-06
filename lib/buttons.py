from machine import Pin
from fifo import Fifo

class Encoder:
    def __init__(self, rot_a, rot_b, rot_btn=None):
        self.a = Pin(rot_a, mode=Pin.IN, pull=Pin.PULL_UP)
        self.b = Pin(rot_b, mode=Pin.IN, pull=Pin.PULL_UP)
        self.fifo = Fifo(30, typecode='i')
        self.a.irq(handler=self.handler, trigger=Pin.IRQ_RISING, hard=True)

        if rot_btn is not None:
            self.btn = Pin(rot_btn, mode=Pin.IN, pull=Pin.PULL_UP)
            # self.btn.irq(handler=self.button_handler, trigger=Pin.IRQ_FALLING)
        else:
            self.btn = None

    def handler(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

    def button_handler(self, pin):
        import utime
        utime.sleep_ms(20)
        if not pin.value():
            print("Button pressed!")

rot = Encoder(10, 11, 12)
