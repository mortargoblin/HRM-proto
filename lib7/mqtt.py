from umqtt.simple import MQTTClient
import ubinascii, machine, network, ntptime, time
import uasyncio as asyncio
class MQTTManager:
    def __init__(self):
        self.client = None
        self.connected = False
        
        # mqtt Config
        self.mac_add = ''
        self.MQTT_BROKER = '192.168.7.253'
        self.MQTT_PORT = 21883 
        self.MQTT_USER = 'Rizvan'
        self.MQTT_PASS = 'Group_6Group_7'
        self.CLIENT_ID = b'hr_monitor_' + ubinascii.hexlify(machine.unique_id())
        

        #topics
        self.TOPIC_HR = b'hr_monitor/heart_rate'
        self.TOPIC_HRV = b'hr_monitor/hrv_data'
        self.TOPIC_STATUS = b'hr_monitor/status'
        self.TOPIC_KUBIOS_REQUEST = b'kubios/request'
        self.TOPIC_KUBIOS_RESPONSE = b'kubios/response'
      
    def connect_mqtt(self):
        try:
            if self.MQTT_USER:
                self.client = MQTTClient(self.CLIENT_ID, self.MQTT_BROKER, 
                                       port=self.MQTT_PORT, 
                                       user=self.MQTT_USER, 
                                       password=self.MQTT_PASS,
                                       )
            else:
                self.client = MQTTClient(self.CLIENT_ID, self.MQTT_BROKER, 
                                       port=self.MQTT_PORT)
            
            print("Connecting to MQTT:", self.MQTT_BROKER, self.MQTT_PORT)
            self.client.connect()
            self.connected = True
            print("MQTT connected.")
            
            self.client.publish(self.TOPIC_STATUS, b"online")
            
            return True
            
        except Exception as e:
            print("MQTT Connection failed:", e)
            self.connected = False
            return False
    
    def publish(self, topic, message):
        try:
            if not self.client or not self.connected:
                if not self.connect_mqtt():
                    print("MQTT reconnect failed, can't publish.")
                    return False
            
            self.client.publish(topic, message)
            print("Publish successful.")
            return True
        
        except Exception as e:
            print("MQTT Publish failed:", e)
            self.connected = False
            return False
    
    def disconnect(self):
        if self.client and self.connected:
            try:
                self.client.publish(self.TOPIC_STATUS, b"offline")
                self.client.disconnect()
            except:
                pass
            self.connected = False
    
    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect("KME_759_Group_7", "Group_6Group_7")
        
        for _ in range(1000):
            if wlan.isconnected():
                print("WiFi Connected:", wlan.ifconfig())
                ntptime.host = 'pool.ntp.org'
                ntptime.settime()
                wlan_mac = wlan.config('mac')
                self.mac_add = f'{wlan_mac.hex().upper()}'
                print("MAC: ", self.mac_add)
                return True
            time.sleep(0.05)

        print("WiFi connection failed")
        return False

    def wait_for_kubios_result(self, timeout=10):
        if not self.connected or not self.client:
            if not self.connect_mqtt():
                return None

        result = {"value": None}

        def callback(topic, msg):
            try:
                if topic == self.TOPIC_KUBIOS_RESPONSE:
                    result["value"] = msg.decode()
            except Exception as e:
                print("Kubios callback error:", e)

        try:
            self.client.set_callback(callback)
            self.client.subscribe(self.TOPIC_KUBIOS_RESPONSE)
        except Exception as e:
            print("Subscribe failed:", e)
            return None

        start = time.time()
        while result["value"] is None and (time.time() - start < timeout):
            try:
                self.client.check_msg()
            except Exception as e:
                print("Error while waiting kubios result:", e)
                break
            time.sleep(0.1)
        print(result["value"])
        return result["value"]

            
    def check_connection(self):
        try:
            if self.connected and self.client:
                return True
            return False
        
        except Exception as e:
            return f"Exception occurred: {e}"