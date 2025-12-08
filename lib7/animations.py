import time
import framebuf
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import uasyncio as asyncio

class Animations:
    def __init__(self, oled):
        self.oled = oled
    
    async def loading_animation(self):
        frames = ['|', '/', '-', '\\']
        start_time = time.time()
        frame = 0
        
        while True:
            self.oled.fill(0)
            self.oled.text("Loading", 40, 20)
            self.oled.text(frames[frame % 4], 60, 40)
            self.oled.show()
            frame += 1
            await asyncio.sleep(0.05)
            
    
    def pulsing_heart(self, x=54, y=20, duration=1):
        heart_frames = [
            [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
            [0x00,0x66,0xFF,0xFF,0xFF,0x7E,0x3C,0x18],
            [0x18,0x7E,0xFF,0xFF,0xFF,0xFF,0x7E,0x3C],
            [0x3C,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0x7E]
        ]
        
        start_time = time.time()
        frame = 0
        
        while time.time() - start_time < duration:
            self.oled.fill(0)
            heart = framebuf.FrameBuffer(bytearray(heart_frames[frame % 4]), 8, 8, framebuf.MONO_HLSB)
            self.oled.blit(heart, x, y)
            self.oled.text("Measuring", 40, 40)
            self.oled.show()
            time.sleep(0.3)
            frame += 1
    
    def slide_transition(self, direction="right"):
        for i in range(0, 128, 8):
            if direction == "right":
                self.oled.scroll(-8, 0)
            elif direction == "left":
                self.oled.scroll(8, 0)
            elif direction == "up":
                self.oled.scroll(0, -8)
            elif direction == "down":
                self.oled.scroll(0, 8)
            self.oled.show()
            time.sleep(0.01)

    def enabling_error_animation(self, mode, state):
        self.oled.fill(0)
        msg = ['[Exception]']      
        x = 15

        if mode == state.HRV:
            msg = ['[Wi-Fi]', 'Error']
            x = 38
            y = 8
        elif mode == state.KUBIOS:
            msg = ['[Wi-Fi/MQTT]', 'Error']
            x = 16
            y = 30
        for i in range(len(msg)):
            self.oled.text(f'{msg[i]}', x + (i*y), 22 + (i*8), 1)
        
        self.oled.show()
        time.sleep(1)
