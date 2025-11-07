from lib7 import buttons, draw

class MenuState:
    HR_DISPLAY: int = 0
    OPTION_2: int = 1
    OPTION_3: int = 2

ENCODER = buttons.Encoder(10, 11, 12)
NUM_OPTIONS = 3

def main():

    current_state = MenuState.HR_DISPLAY

    ### MAIN LOOP ###
    while True:

        fifo = int(ENCODER.fifo.empty())

        # input handling

        if not fifo:
            fifo_value = ENCODER.fifo.get()
            if fifo_value == 1:
                current_state = (current_state + 1) % NUM_OPTIONS
            elif fifo_value == -1:
                current_state = (current_state - 1) % NUM_OPTIONS

            draw.menu(current_state)


if __name__=="__main__":
    main()
