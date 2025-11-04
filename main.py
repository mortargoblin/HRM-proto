from machine import Pin
import sys

print(sys.path)

import Rotatory

class MenuState:
    HR_DISPLAY: int = 0
    OPTION_2: int = 1
    OPTION_3: int = 2

NUM_MENU_STATES: int = 3
current_state = MenuState.HR_DISPLAY

def main():

    ### MAIN LOOP ###
    while True:

        # input handling
        print(Rotatory.Encoder.value(), "VALUE")

        # next menu option
        if Rotatory.Encoder.value() == 1:
            current_state = (current_state + 1) % NUM_MENU_STATES


if __name__=="__main__":
    main()
