from machine import Pin
from lib7 import buttons, draw
import micropython

micropython.alloc_emergency_exception_buf(200)

class MenuState:
    HR_DISPLAY: int = 0
    OPTION_2: int = 1
    OPTION_3: int = 2

Encoder = buttons.Encoder(10, 11, 12)
ReturnBtn = buttons.Return(9, Pin.IN, Pin.PULL_UP)
# sw_0 = Pin(9, mode = Pin.IN, pull = Pin.PULL_UP)

NUM_OPTIONS = 3

def main():

    current_state = MenuState.HR_DISPLAY

    ### MAIN LOOP ###
    while True:
        draw.menu(current_state)

        fifo = int(Encoder.fifo.empty())

        # rotary encoder rotation handling
        if not fifo:
            fifo_value = Encoder.fifo.get()
            if fifo_value == 1:
                current_state = (current_state + 1) % NUM_OPTIONS
            elif fifo_value == -1:
                current_state = (current_state - 1) % NUM_OPTIONS

        
        # rotary encoder button handling
        if Encoder.pressed:
            launch(current_state)
            Encoder.pressed = False

        if ReturnBtn.pressed:
            ReturnBtn.pressed = False

def launch(option: int):
    if option == MenuState.HR_DISPLAY:
        while ReturnBtn.pressed == False:
            # launch HR_DISPLAY
            draw.display_pulse()

if __name__=="__main__":
    main()
