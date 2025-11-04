from machine import Pin
import sys

print(sys.path)

import Rotatory

class MenuState:
    HR_DISPLAY: int = 0
    OPTION_2: int = 1
    OPTION_3: int = 2

def main():

    ### MAIN LOOP ###
    while True:

        # input handling
        print(Rotatory.Encoder.value(), "VALUE")


if __name__=="__main__":
    main()
