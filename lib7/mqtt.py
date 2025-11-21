from umqtt.simple import MQTTClient

WIFI_SSID = 'YourSSID'
WIFI_PASS = 'YourPassword'

MQTT_BROKER = '192.168.1.10'   # brokerin IP tai hostname
MQTT_PORT = 1883
MQTT_USER = 'username'         # jos ei käytössä, laita None
MQTT_PASS = 'password'         # jos ei käytössä, laita None
CLIENTID = b'client' + ubinascii.hexlify(machine.unique_id())

TOPIC = b'game/players/player123/state'
def make_client():
    if MQTT_USER:
        return MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASS)
    else:
        return MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)