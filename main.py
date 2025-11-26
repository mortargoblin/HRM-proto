from machine import Pin
from lib7 import buttons, hrlib, kubios
import micropython

micropython.alloc_emergency_exception_buf(200)

class MenuState:
    HR_DISPLAY: int = 0
    HRV: int = 1
    HISTORY: int = 2
    KUBIOS: int = 3

Encoder = buttons.Encoder(10, 11, 12)
ReturnBtn = buttons.Return(9, Pin.IN, Pin.PULL_UP)
Kubios = kubios.KubiosAnalytics()

# sw_0 = Pin(9, mode = Pin.IN, pull = Pin.PULL_UP)

NUM_OPTIONS = 4

def main():
    current_state = MenuState.HR_DISPLAY

     # Testing for Wi-Fi connection:
    wifi_connected = kubios.mqtt_manager.connect_wifi()
        
    if wifi_connected:
        print("Connected to a Wi-Fi.")
        
    else:
        print("Cannot connect to a Wi-Fi.")


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
        hrlib.hr_monitor(ReturnBtn = ReturnBtn, mode ="hr", Kubios=Kubios)

    elif option == MenuState.HRV:
        hrlib.hr_monitor(ReturnBtn = ReturnBtn, mode = "hrv", Kubios=Kubios)
  

    elif option == MenuState.HISTORY:
        #hrlib.get_Med_History(ReturnBtn = ReturnBtn, Encoder = Encoder, mode = "hist")    
        pass
        
    elif option == MenuState.KUBIOS:
        #launch Kubios analytics
        if Kubios.enabled:
            Kubios.disable()
            print("Kubios disabled")
        else:
            if Kubios.enable():
                print("Kubios enabled! Data will be sent to cloud")
            else:
                print("Failed to enable kubios, check WiFi/MQTT connection")

if __name__=="__main__":
    main()
