from machine import Pin
from lib7 import buttons, hrlib, kubios, mqtt
import micropython

micropython.alloc_emergency_exception_buf(200)

class MenuState:
    HR_DISPLAY: int = 0
    HRV: int = 1
    HISTORY: int = 2
    KUBIOS: int = 3

Encoder = buttons.Encoder(10, 11, 12)
ReturnBtn = buttons.Return(9, Pin.IN, Pin.PULL_UP)
Mqtt_broker = mqtt.MQTTManager()
# sw_0 = Pin(9, mode = Pin.IN, pull = Pin.PULL_UP)

NUM_OPTIONS = 4

def main():
    current_state = MenuState.HR_DISPLAY

    # Testing for Wi-Fi connection:
    print("Connecting to Wi-Fi...")
    wifi_connected = Mqtt_broker.connect_wifi()
        
    if wifi_connected:
        print("Initializing MQTT...")
        
        mqtt_connected = Mqtt_broker.connect()
        if mqtt_connected:
            print("MQTT connected successfully!")
            kubios.mqtt_manager.publish("test", "[Connected]")
        else:
            print("MQTT connection failed")
    else:
        print("Cannot connect MQTT - no WiFi connection")

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
        hrlib.hr_monitor(ReturnBtn = ReturnBtn, mode ="hr")

    elif option == MenuState.HRV:
        hrlib.hr_monitor(ReturnBtn = ReturnBtn, mode = "hrv")
  

    elif option == MenuState.HISTORY:
        #hrlib.get_Med_History(ReturnBtn = ReturnBtn, Encoder = Encoder, mode = "hist")    
        pass
        
    elif option == MenuState.KUBIOS:
        # # launch Kubios analytics
        if kubios.enabled:
            kubios.disable()
            print("Kubios disabled")
        else:
            if kubios.enable():
                print("Kubios enabled! Data will be sent to cloud")
            else:
                print("Failed to enable kubio, check WiFi/MQTT connection")
        return

if __name__=="__main__":
    main()
