from lib7.mqtt import MQTTManager
from lib7 import history, menu_icons
import json
import time
import framebuf

class KubiosAnalytics:  
    def __init__(self):
        self.enabled: bool = False
        self.data_buffer = []
        self.mqtt_manager = MQTTManager()
        
    def enable(self):
        try:
            if not self.mqtt_manager.connect_wifi():
                print("Wifi Error occurred.")
                return False
            
            if not self.mqtt_manager.connect_mqtt():
                print("Kubios not connected due to an MQTT Error.")
                return False
            
            self.enabled = True
            print("Kubios ON")
            return True
        
        except Exception as e:
            print(f"Exception occurred: {e}")
            return False
    
    def send_hrv_data(self, avg_ppi_list):
        MAC = self.mqtt_manager.mac_add
        print("CLEAN PPI LIST: ", avg_ppi_list)
        data = {
            "mac": f'{MAC}',
            "type": "RRI",
            "data": avg_ppi_list,
            "analysis": {"type": "readiness"}
        }
        message = json.dumps(data)
        print(type(message))
        try:
            payload_sent = self.mqtt_manager.publish(self.mqtt_manager.TOPIC_KUBIOS_REQUEST, message)

            if payload_sent:
                print(f"HRV data sent to Kubios: {avg_ppi_list}")
            return payload_sent

        except Exception as e:
            print(f"Failed to send HRV data: {e}")
            return False
                
    def select_and_send(self, ReturnBtn, Encoder):
        """if not self.enabled:
            print("Kubios not enabled")
            return"""

        records = {}
        try:
            with open('patient_records.txt', 'r') as file:
                lines = 0
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    line = line[1:-1]
                    record = line.split(", ")
                    records[f"Patient[{lines+1}]"] = record
                    lines += 1
        except Exception as e:
            print(f"Error loading patient records: {e}")
            return

        if not records:
            print("No patient records found.")
            return

        def draw_kubios_select(counter):
            oled = history.oled
            icons = menu_icons.Kubios_Icons()
            person_icon = icons[0]
            icon_fb = framebuf.FrameBuffer(person_icon, 12, 12, framebuf.MONO_HLSB)

            oled.fill(0)
            oled.text("[Kubios]", 0, 0, 1)
            oled.text("Select patient", 0, 10, 1)

            start_y = 24
            step_y = 10
            max_index = len(records)

            for i in range(1, max_index + 1):
                y = start_y + (i - 1) * step_y

                #icon
                oled.blit(icon_fb, 0, y - 2)

                label = f"Patient {i}"

                #arrow
                if i == counter:
                    oled.text(">", 14, y)
                else:
                    oled.text(" ", 14, y)

                oled.text(label, 24, y)

            oled.show()

        counter = 1
        max_index = len(records)
        draw_kubios_select(counter)

        while not ReturnBtn.pressed:
            #rotary movement
            if Encoder.fifo.has_data():
                rotator = Encoder.fifo.get()
                if rotator == 1 and counter < max_index:
                    counter += 1
                    draw_kubios_select(counter)
                elif rotator == -1 and counter > 1:
                    counter -= 1
                    draw_kubios_select(counter)

            #Press to send corresponding patient's ppi-list to Kubios Cloud:
            if Encoder.pressed:
                key = f"Patient[{counter}]"
                values = records[key]

                try:
                    clean_ppi_list = [int(''.join(filter(str.isdigit, item))) for item in values[5:]]
                    print(clean_ppi_list)
                
                except Exception as e:
                    print("Failed to parse patient record:", e)
                    Encoder.pressed = False
                    continue

                oled = history.oled

                # show loading
                oled.fill(0)
                oled.text("[Kubios]", 0, 0, 1)
                oled.text(f"Sending Patient {counter}", 0, 20, 1)
                oled.show()

                print("Sending to Kubios:", clean_ppi_list)
                success = self.send_hrv_data(clean_ppi_list)

                if not success:
                    #show result
                    oled.fill(0)
                    oled.text("[Kubios]", 0, 0, 1)
                    oled.text("Error sending", 0, 20, 1)
                    oled.show()
                    time.sleep(1)

                    #back to selection
                    Encoder.pressed = False
                    draw_kubios_select(counter)
                    continue

                #Wait for kubios result
                oled.fill(0)
                oled.text("[Kubios]", 0, 0, 1)
                oled.text("Waiting result", 0, 20, 1)
                oled.show()

                response = None
                if hasattr(self.mqtt_manager, "wait_for_kubios_result"):
                    response = self.mqtt_manager.wait_for_kubios_result(timeout=10)

                #Display result
                oled.fill(0)
                oled.text("[Kubios]", 0, 0, 1)

                if response:
                    oled.text("Result:", 0, 12, 1)
                    resp_str = str(response)
                    oled.text(resp_str[:16], 0, 22, 1)
                    oled.text(resp_str[16:32], 0, 32, 1)
                else:
                    oled.text("No response", 0, 20, 1)

                oled.show()
                time.sleep(3)

                #Backs up to selecting a patient
                Encoder.pressed = False
                draw_kubios_select(counter)

        ReturnBtn.pressed = False