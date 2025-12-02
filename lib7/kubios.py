from lib7.mqtt import MQTTManager
import json
import time

class KubiosAnalytics:
    
    def __init__(self):
        self.enabled: bool = False
        self.data_buffer = []
        self.mqtt_manager = MQTTManager()#instance
        
    def enable(self):
        try:
            if not self.mqtt_manager.connect_wifi():
                print("Failed to connect WiFi for Kubios")
                return False
            
            if not self.mqtt_manager.connect_mqtt():
                print("Failed to connect MQTT for Kubios")
                return False
            
            self.enabled = True
            print("Kubios analytics enabled")
            return True
        
        except Exception as e:
            print(f"Failed to enable Kubios: {e}")
            return False
    
    def disable(self): #disable kubios cloud services
        self.enabled = False
        print("Kubios analytics disabled")
    
    def send_hr_data(self, bpm, ppi_list=None): #append heart rate data to Kubios
        if not self.enabled:
            print("Kubios not enabled")
            return False
            
        data = {
            "bpm": bpm,
            "timestamp": time.time()
        }
        
        if ppi_list:
            data["ppi"] = ppi_list
        
        try:
            message = json.dumps(data)
            success = self.mqtt_manager.publish(self.mqtt_manager.TOPIC_HR, message)
            if success:
                print(f"HR data sent to Kubios: {bpm} BPM")
            return success
        except Exception as e:
            print(f"Failed to send HR data: {e}")
            return False
    
    def send_hrv_data(self, mean_ppi, mean_bpm, sdnn, rmssd):#append HRV analysis data to kubios
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
            success = self.mqtt_manager.publish(self.mqtt_manager.TOPIC_HRV, message)
            if success:
                print(f"HRV data sent to Kubios: BPM={mean_bpm}, SDNN={sdnn}")
            return success
        except Exception as e:
            print(f"Failed to send HRV data: {e}")
            return False

