import datetime
import json

import paho.mqtt.client as mqtt

from units import convert_f_to_c, convert_c_to_k, convert_mps_to_mph
from meteorological import dew_point, heat_index, wind_chill, frost_point


class MQTTClient:
    def __init__(self, mqtt_host, mqtt_username, mqtt_password, input_topic_weather, input_topic_indoor, output_topic):
        self.output_data = {}

        self.mqtt_host = mqtt_host
        self.input_topic_weather = input_topic_weather
        self.input_topic_indoor = input_topic_indoor
        self.output_topic = output_topic

        self.client = mqtt.Client()
        self.client.username_pw_set(mqtt_username, mqtt_password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def start(self):
        self.client.connect(self.mqtt_host, 1883, 60)
        self.client.loop_forever()

    def stop(self):
        self.client.disconnect()

    # Define the on_message function for the MQTT client
    def on_message(self, client, userdata, message):
        # Get the message payload as a JSON string
        payload = message.payload.decode('utf-8')

        # Convert the JSON string to a Python dictionary
        data = json.loads(payload)

        # Determine which input topic the message came from and update the output data accordingly
        if message.topic == self.input_topic_weather:
            self.output_data["outTempBatteryStatus"] = 0 if data["battery_ok"] else 1
            self.output_data["outTemp"] = round(convert_f_to_c(data["temperature_F"]), 1)
            self.output_data["outHumidity"] = data["humidity"]
            self.output_data["windDir"] = data["wind_dir_deg"]
            self.output_data["windSpeed"] = data["wind_avg_m_s"]
            self.output_data["windGust"] = data["wind_max_m_s"]
            self.output_data["rain"] = data["rain_mm"]
            self.output_data["UV"] = data["uv"]/10
            self.output_data["outRSSI"] = data["rssi"]
            self.output_data["outSNR"] = data["snr"]
            self.output_data["outNoise"] = data["noise"]

            utc_time = datetime.datetime.strptime(data["time"], '%Y-%m-%d %H:%M:%S')
            local_tz = datetime.datetime.now().astimezone().tzinfo
            local_time = utc_time.replace(tzinfo=datetime.timezone.utc).astimezone(local_tz)
            self.output_data["outTime"] = int(local_time.timestamp())

            self.output_data["heatindex"] = round(convert_f_to_c(heat_index(data["temperature_F"], data["humidity"])), 1)
            self.output_data["windchill"] = round(convert_f_to_c(wind_chill(data["temperature_F"], convert_mps_to_mph(data["wind_avg_m_s"]))), 1)
            self.output_data["dewpoint"] = round(convert_f_to_c(dew_point(data["temperature_F"], data["humidity"])), 1)
            self.output_data["frostpoint"] = round(
                convert_f_to_c(frost_point(
                    convert_c_to_k(self.output_data["outTemp"]),
                    convert_c_to_k(self.output_data["dewpoint"]))
                ), 1)
        elif message.topic == self.input_topic_indoor:
            self.output_data["inTempBatteryStatus"] = 0 if data["battery_ok"] else 1
            self.output_data["inTemp"] = round(convert_f_to_c(data["temperature_F"]), 1)
            self.output_data["inHumidity"] = data["humidity"]
            self.output_data["inRSSI"] = data["rssi"]
            self.output_data["inSNR"] = data["snr"]
            self.output_data["inNoise"] = data["noise"]

            utc_time = datetime.datetime.strptime(data["time"], '%Y-%m-%d %H:%M:%S')
            local_tz = datetime.datetime.now().astimezone().tzinfo
            local_time = utc_time.replace(tzinfo=datetime.timezone.utc).astimezone(local_tz)
            self.output_data["inTime"] = int(local_time.timestamp())

        # Publish the updated output data as a JSON string on the output topic
        client.publish(self.output_topic, json.dumps(self.output_data))

    # Define the on_connect function for the MQTT client
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        # Subscribe to the input topics
        client.subscribe(self.input_topic_weather)
        client.subscribe(self.input_topic_indoor)

    # Define the on_disconnect function for the MQTT client
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            raise Exception("MQTT disconnection")
