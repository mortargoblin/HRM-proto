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
    
    def disable(self):
        self.enabled = False
        print("Kubios analytics disabled")
    
    def send_hrv_data(self, mean_ppi, mean_bpm, sdnn, rmssd):
        if not self.enabled:
            print("Kubios not enabled")
            return False
            
        data = {
            "mean_ppi": mean_ppi,
            "mean_bpm": mean_bpm,
            "sdnn": sdnn,
            "rmssd": rmssd,
            "timestamp": time.time()
        }
        
        try:
            message = json.dumps(data)
            success = self.mqtt_manager.publish("kubios/request", message)
            if success:
                print(f"HRV data sent to Kubios: BPM={mean_bpm}, SDNN={sdnn}")
            return success
        except Exception as e:
            print(f"Failed to send HRV data: {e}")
            return False
                
            data = {
                "mean_ppi": mean_ppi,
                "mean_bpm": mean_bpm,
                "sdnn": sdnn,
                "rmssd": rmssd,
                "timestamp": time.time()
            }
            
            try:
                message = json.dumps(data)
                success = self.mqtt_manager.publish(self.mqtt_manager.TOPIC_HRV, message)
                if success:
                    print(f"HRV data sent to Kubios: BPM={mean_bpm}, SDNN={sdnn}")
                return success
            except Exception as e:
                print(f"Failed to send HRV data: {e}")
                return False

    def select_and_send(self, ReturnBtn, Encoder):
        if not self.enabled:
            print("Kubios not enabled")
            return

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
            oled.text("[Select]", 65, 0, 1)

            start_y = 12
            step_y = 10
            max_index = len(records)

            for i in range(1, max_index + 1):
                y = start_y + (i - 1) * step_y

                #icon
                oled.blit(icon_fb, 0, y - 2)

                label = f"P-{i}"

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

            #press to send this patient to Kubios
            if Encoder.pressed:
                key = f"Patient[{counter}]"
                values = records[key]

                #values structure is like
                #["'25/11/2025'", "'AVG_BPM: 69'", "'AVG_PPI: 22'", "'RMSSD: 10'", "'SDNN: 03'"]
                try:
                    date_str = values[0].strip("'")
                    mean_bpm = int(values[1].strip("'").split(":")[1].strip())
                    mean_ppi = int(values[2].strip("'").split(":")[1].strip())
                    rmssd = int(values[3].strip("'").split(":")[1].strip())
                    sdnn = int(values[4].strip("'").split(":")[1].strip())
                except Exception as e:
                    print("Failed to parse patient record:", e)
                    Encoder.pressed = False
                    continue

                oled = history.oled

                # show loading
                oled.fill(0)
                oled.text("[Kubios]", 0, 0, 1)
                oled.text(f"Sending P-{counter}", 0, 20, 1)
                oled.text(date_str, 0, 30, 1)
                oled.show()

                print("Sending to Kubios:", date_str, mean_bpm, mean_ppi, rmssd, sdnn)
                success = self.send_hrv_data(mean_ppi, mean_bpm, sdnn, rmssd)

                #show result
                oled.fill(0)
                oled.text("[Kubios]", 0, 0, 1)
                if success:
                    oled.text("Done", 0, 20, 1)
                else:
                    oled.text("Error sending", 0, 20, 1)
                oled.show()
                time.sleep(1)

                #back to selection
                Encoder.pressed = False
                draw_kubios_select(counter)

        ReturnBtn.pressed = False