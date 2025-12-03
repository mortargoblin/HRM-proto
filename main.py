from machine import Pin
from lib7 import buttons, hrlib, kubios, mqtt, history
import micropython, framebuf
import time

micropython.alloc_emergency_exception_buf(200)

class MenuState:
    HR_DISPLAY: int = 0
    HRV: int = 1
    KUBIOS: int = 2
    HISTORY: int = 3

Encoder = buttons.Encoder(10, 11, 12)
ReturnBtn = buttons.Return(9, Pin.IN, Pin.PULL_UP)
Mqtt = mqtt.MQTTManager()
Kubios = kubios.KubiosAnalytics()

NUM_OPTIONS = 4

def main():
    current_state = MenuState.HR_DISPLAY

    # Testing for Wi-Fi connection:
    wifi_connected = Mqtt.connect_wifi()
        
    if wifi_connected:
        mqtt_connected = Mqtt.connect_mqtt()
        if mqtt_connected:
            print("MQTT: OK\nWIFI: OK")  
        else:
            print("MQTT: FAIL\nWIFI: OK")  
    else:
        print("Cannot connect to a Wi-Fi.")


    ### MAIN LOOP ###
    while True:
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
            launch(current_state)
            Encoder.pressed = False
            ReturnBtn.pressed = False

        if ReturnBtn.pressed:
            ReturnBtn.pressed = False

def launch(option: int):
    if option == MenuState.HR_DISPLAY:
        hrlib.hr_monitor(ReturnBtn=ReturnBtn, mode="hr", Mqtt=Mqtt)
        

    elif option == MenuState.HRV:
        hrlib.hr_monitor(ReturnBtn=ReturnBtn, mode="hrv", Mqtt=Mqtt)
        

    elif option == MenuState.KUBIOS:
        k_status = Kubios.enable()
        
        if Kubios.enabled:
            hrlib.oled.fill(0)
            hrlib.oled.text(f'{k_status}', 15, 30, 1)
            hrlib.oled.show()
            time.sleep(1)
            #TÄHÄN FUNKTIOKUTSU
            Kubios.disable()
        
        else:
            hrlib.oled.fill(0)
            hrlib.oled.text(f'{k_status}', 15, 30, 1)
            hrlib.oled.show()
            time.sleep(1)
            
        
    elif option == MenuState.HISTORY:
        history.get_Med_History(ReturnBtn=ReturnBtn, Encoder=Encoder)
        
if __name__=="__main__":
    main()
