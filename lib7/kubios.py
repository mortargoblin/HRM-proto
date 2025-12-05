from lib7.mqtt import MQTTManager
from lib7 import history
import json
import time

class KubiosAnalytics:
    
    def __init__(self):
        self.enabled: bool = False
        self.data_buffer = []
        self.mqtt_manager = MQTTManager()
        
    def enable(self):
        try:
            if not self.mqtt_manager.connect_wifi():
                print("Wifi Error occurred.")
                return "[Wi-fi Error]"
            
            if not self.mqtt_manager.connect_mqtt():
                print("Kubios not connected due to an MQTT Error.")
                return "[MQTT Error]"
            
            self.enabled = True
            print("Kubios ON")
            return "[Kubios ON]"
        
        except Exception as e:
            print(f"Exception occurred: {e}")
            return "[SYS ERROR]"
    
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

        counter = 1
        history.update_Display(records, counter)

        while not ReturnBtn.pressed:
            #rotary movement
            if Encoder.fifo.has_data():
                rotator = Encoder.fifo.get()
                max_index = len(records)
                if rotator == 1 and counter < max_index:
                    counter += 1
                    history.update_Display(records, counter)
                elif rotator == -1 and counter > 1:
                    counter -= 1
                    history.update_Display(records, counter)

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

                print("Sending to Kubios:", date_str, mean_bpm, mean_ppi, rmssd, sdnn)
                self.send_hrv_data(mean_ppi, mean_bpm, sdnn, rmssd)
                Encoder.pressed = False

        ReturnBtn.pressed = False