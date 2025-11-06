from lib import buttons, draw

class MenuState:
    HR_DISPLAY: int = 0
    OPTION_2: int = 1
    OPTION_3: int = 2

ENCODER = buttons.Encoder(10, 11, 12)
NUM_OPTIONS = 3

def main():

    current_state = MenuState.HR_DISPLAY

    fifo = int(ENCODER.fifo.empty())

    ### MAIN LOOP ###
    while True:

        # input handling

        if not fifo:
            fifo_value = rot.fifo.get()
            if fifo_value == 1:
                current_state = (current_state + 1) % NUM_OPTIONS
            elif fifo_value == -1:
                current_state = (current_stte -1) % NUM_OPTIONS

            draw.cursor(current_state)

        print("state", current_state)


if __name__=="__main__":
    main()
