from lib7.mqtt import MQTTManager


import json
import time
from lib7 import mqtt
mqtt_manager = mqtt.MQTTManager()

class KubiosAnalytics:
    
    def __init__(self):
        self.enabled: bool = False
        self.data_buffer = []
        
    def enable(self):
        if mqtt_manager.check_connection(): #enable kubios cloud services
            self.enabled = True
            print("Kubios analytics enabled")
            
            return True
        else:
            print("Failed to enable Kubios - MQTT not connected")
            return False
    
    def disable(self): #disable kubios cloud services
        self.enabled = False
        print("Kubios analytics disabled")
    
    def send_hr_data(self, bpm, ppi_list=None): #append heart rate data to Kubios
        if not self.enabled:
            return False
            
        data = {
            "bpm": bpm,
            "timestamp": time.time()
        }
        
        if ppi_list:
            data["ppi"] = ppi_list
        
        try:
            message = json.dumps(data)
            return mqtt_manager.publish(mqtt_manager.TOPIC_HR, message)
        except Exception as e:
            print("Failed to send HR data:", e)
            return False
    
    def send_hrv_data(self, mean_ppi, mean_bpm, sdnn, rmssd):#append HRV analysis data to kubios
        if not self.enabled:
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
            return mqtt_manager.publish(mqtt_manager.TOPIC_HRV, message)
        except Exception as e:
            print("Failed to send HRV data:", e)
            return False
