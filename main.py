from machine import Pin
from lib7 import buttons, hrlib
import micropython

micropython.alloc_emergency_exception_buf(200)

class MenuState:
    HR_DISPLAY: int = 0
    ADVANCED: int = 1
    HISTORY: int = 2
    KUBIOS: int = 3

Encoder = buttons.Encoder(10, 11, 12)
ReturnBtn = buttons.Return(9, Pin.IN, Pin.PULL_UP)
# sw_0 = Pin(9, mode = Pin.IN, pull = Pin.PULL_UP)

NUM_OPTIONS = 4

def main():

    current_state = MenuState.HR_DISPLAY

    ### MAIN LOOP ###
    while True:
        hrlib.menu(current_state)

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
        # launch HR_DISPLAY
        hrlib.hr_monitor(ReturnBtn, True)

    elif option == MenuState.ADVANCED:
        #Launch advanced measurements mode
        return

    elif option == MenuState.HISTORY:
        #Launch history view mode
        return

    elif option == MenuState.KUBIOS:
        # Launch Kubios anal
        return

if __name__=="__main__":
    main()
