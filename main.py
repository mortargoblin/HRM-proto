from machine import Pin
from lib7 import buttons, hrlib, kubios, mqtt, history
import micropython
import time

micropython.alloc_emergency_exception_buf(200)

class MenuState:
    HR_DISPLAY: int = 0
    HRV: int = 1
    KUBIOS: int = 2
    HISTORY: int = 3

Encoder = buttons.Encoder(10, 11, 12)

#Button for exiting a mode in an instant:
ReturnBtn = buttons.Utility(9, Pin.IN, Pin.PULL_UP)

#Class for handling MQTT + Wi-Fi functionality
Mqtt = mqtt.MQTTManager()

Kubios = kubios.KubiosAnalytics()

NUM_OPTIONS = 4

def main():
    current_state = MenuState.HR_DISPLAY

    ### MAIN LOOP ###
    while True:

        Encoder.enabled = True
        hrlib.menu(current_state)

        # rotary encoder rotation handling
        if not Encoder.fifo.empty():
            fifo_value = Encoder.fifo.get()
            if fifo_value == 1:
                current_state = (current_state + 1) % NUM_OPTIONS
            elif fifo_value == -1:
                current_state = (current_state - 1) % NUM_OPTIONS

        # rotary encoder button handling
        if Encoder.pressed:
            Encoder.pressed = False
            launch(current_state)

        if ReturnBtn.pressed:
            ReturnBtn.pressed = False

def launch(option: int):
    if option == MenuState.HR_DISPLAY:
        print("Encoder.pressed:", Encoder.pressed)
        hrlib.hr_monitor(ReturnBtn=ReturnBtn, Encoder=Encoder, mode="hr", Mqtt=Mqtt)

    elif option == MenuState.HRV:
        if Mqtt.connect_wifi():
            hrlib.hr_monitor(ReturnBtn=ReturnBtn, Encoder=Encoder, mode="hrv", Mqtt=Mqtt)
        else:
            hrlib.oled.fill(0)
            hrlib.oled.text('[Wi-Fi Error]', 15, 30, 1)
            hrlib.oled.show()
            time.sleep(1)
            
    elif option == MenuState.KUBIOS:
        k_status = Kubios.enable()
    
        if Kubios.enabled:
            Kubios.select_and_send(ReturnBtn=ReturnBtn, Encoder=Encoder)
        else:
            hrlib.oled.fill(0)
            hrlib.oled.text(f"{k_status}", 15, 30, 1)
            hrlib.oled.show()
            time.sleep(1)

    elif option == MenuState.HISTORY:
        history.get_Med_History(ReturnBtn=ReturnBtn, Encoder=Encoder)
        
if __name__=="__main__":
    main()
