from umqtt.simple import MQTTClient
import ubinascii, machine, time, network

class MQTTManager:
    def __init__(self):
        self.client = None
        self.connected = False
        
        #mqtt Config
        self.MQTT_BROKER = '192.168.7.253'
        self.MQTT_PORT = 21883
        self.MQTT_USER = 'sami'
        self.MQTT_PASS = 'Group_6Group_7'
        self.CLIENT_ID = b'hr_monitor_' + ubinascii.hexlify(machine.unique_id())
        
        #topics
        self.TOPIC_HR = 'hr_monitor/heart_rate'
        self.TOPIC_HRV = 'hr_monitor/hrv_data'
        self.TOPIC_STATUS = 'hr_monitor/status'
    
    def connect(self):
        try:
            if self.MQTT_USER:
                self.client = MQTTClient(self.CLIENT_ID, self.MQTT_BROKER, 
                                       port=self.MQTT_PORT, 
                                       user=self.MQTT_USER, 
                                       password=self.MQTT_PASS)
            else:
                self.client = MQTTClient(self.CLIENT_ID, self.MQTT_BROKER, 
                                       port=self.MQTT_PORT)
            
            self.client.connect()
            self.connected = True
            print("MQTT Connected")
            self.publish(self.TOPIC_STATUS, b"online")
            return True
            
        except Exception as e:
            print("MQTT Connection failed:", e)
            self.connected = False
            return False
    
    def publish(self, topic, message):
        if not self.connected or not self.client:
            self.connect()
            
            
        try:
            self.client.publish(topic, message)
            print("Publish successful.")
            
        except Exception as e:
            print("MQTT Publish failed:", e)
            self.connected = False
            
    
    def disconnect(self):
        if self.client and self.connected:
            try:
                self.publish(self.TOPIC_STATUS, b"offline")
                self.client.disconnect()
            except:
                pass
            self.connected = False
    
    def check_connection(self):
        if not self.connected:
            return self.connect()
        return True
    
    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        WIFI_SSID = 'KME_759_Group_7'
        WIFI_PASS = 'Group_6Group_7'
        
        if not wlan.isconnected():
            wlan.connect(WIFI_SSID, WIFI_PASS)
            
            #Wait for connection
            print("Connecting for Wi-Fi", end="")
            for i in range(5):
                if wlan.isconnected():
                    break
                print(".", end="")
                time.sleep(1)
            print()
        
        if wlan.isconnected():
            print('WiFi connected!')
            print('Network config:', wlan.ifconfig())
            return True
        else:
            print('WiFi connection failed')
            return False
