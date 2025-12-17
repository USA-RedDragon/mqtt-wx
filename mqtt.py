from datetime import datetime
import json
import math
import time

import paho.mqtt.client as mqtt

from units import convert_f_to_c, convert_c_to_k, convert_mps_to_mph
from meteorological import dew_point, heat_index, wind_chill, frost_point, cloudbase

TOPIC_PREFIX = "mqtt-wx"
TOPIC_LIGHTNING_COUNT = f"{TOPIC_PREFIX}/lightning_count"


class MQTTClient:

    def __init__(self,
                 mqtt_host,
                 mqtt_username,
                 mqtt_password,
                 input_topic_weather,
                 input_topic_indoor,
                 input_topic_lightning,
                 input_topic_light,
                 input_topic_pressure,
                 input_topic_particle_sensor,
                 input_topic_co2,
                 output_topic):
        self.output_data = {}
        self.previous_output_data = {}

        self.mqtt_host = mqtt_host
        self.input_topic_weather = input_topic_weather
        self.input_topic_co2 = input_topic_co2
        self.input_topic_indoor = input_topic_indoor
        self.input_topic_lightning = input_topic_lightning
        self.input_topic_light = input_topic_light
        self.input_topic_pressure = input_topic_pressure
        self.input_topic_particle_sensor = input_topic_particle_sensor
        self.output_topic = output_topic

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(mqtt_username, mqtt_password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.total_lightning_strikes = -1

        self.rain = -1

    def start(self):
        self.client.connect(self.mqtt_host, 1883, 60)
        self.client.loop_forever()

    def stop(self):
        self.client.disconnect()

    # Define the on_message function for the MQTT client
    def on_message(self, client, userdata, message):
        # Get the message payload as a JSON string
        payload = message.payload.decode('utf-8')
        self.previous_output_data = self.output_data

        if message.topic == TOPIC_LIGHTNING_COUNT:
            if self.total_lightning_strikes == -1:
                self.total_lightning_strikes = int(payload)
                self.client.publish(TOPIC_LIGHTNING_COUNT, str(self.total_lightning_strikes), retain=True)
            self.client.unsubscribe(TOPIC_LIGHTNING_COUNT)
            return

        # Convert the JSON string to a Python dictionary
        data = json.loads(payload)

        # Determine which input topic the message came from and update the output data accordingly
        if message.topic == self.input_topic_weather:
            if "battery_ok" in data and data["battery_ok"] is not None:
                self.output_data["outTempBatteryStatus"] = 0 if data["battery_ok"] else 1
            if "temperature_F" in data and data["temperature_F"] is not None:
                self.output_data["outTemp"] = round(convert_f_to_c(data["temperature_F"]), 1)
            if "humidity" in data and data["humidity"] is not None:
                self.output_data["outHumidity"] = data["humidity"]
            if "wind_dir_deg" in data and data["wind_dir_deg"] is not None:
                self.output_data["windDir"] = data["wind_dir_deg"]
            if "wind_avg_m_s" in data and data["wind_avg_m_s"] is not None:
                self.output_data["windSpeed"] = data["wind_avg_m_s"]
            if "wind_max_m_s" in data and data["wind_max_m_s"] is not None:
                self.output_data["windGust"] = data["wind_max_m_s"]
            if "uv" in data and data["uv"] is not None:
                self.output_data["UV"] = data["uv"]/10
            if "rssi" in data and data["rssi"] is not None:
                self.output_data["outRSSI"] = data["rssi"]
            if "snr" in data and data["snr"] is not None:
                self.output_data["outSNR"] = data["snr"]
            if "noise" in data and data["noise"] is not None:
                self.output_data["outNoise"] = data["noise"]
            # self.output_data["luminosity"] = data["light_lux"]
            if "light_lux" in data and data["light_lux"] is not None:
                self.output_data["radiation"] = data["light_lux"]/126.7

            if "humidity" in data and "temperature_F" in data and data["humidity"] is not None and data["temperature_F"] is not None:
                self.output_data["heatindex"] = round(convert_f_to_c(
                    heat_index(data["temperature_F"], data["humidity"])
                ), 1)
            if "wind_avg_m_s" in data and "temperature_F" in data and data["wind_avg_m_s"] is not None and data["temperature_F"] is not None:
                wc, shouldWC = wind_chill(data["temperature_F"], convert_mps_to_mph(data["wind_avg_m_s"]))
                if shouldWC:
                    self.output_data["windchill"] = round(convert_f_to_c(wc), 1)
                else:
                    if "windchill" in self.output_data:
                        self.output_data.pop("windchill")
            if "temperature_F" in data and "humidity" in data and data["temperature_F"] is not None and data["humidity"] is not None:
                self.output_data["dewpoint"] = round(convert_f_to_c(dew_point(data["temperature_F"], data["humidity"])), 1)
            if "dewpoint" in self.output_data and "outTemp" in self.output_data and self.output_data["dewpoint"] is not None and self.output_data["outTemp"] is not None:
                self.output_data["frostpoint"] = round(
                    convert_f_to_c(frost_point(
                        convert_c_to_k(self.output_data["outTemp"]),
                        convert_c_to_k(self.output_data["dewpoint"]))
                    ), 1)

            if "outTemp" in self.output_data and "dewpoint" in self.output_data and self.output_data["outTemp"] is not None and self.output_data["dewpoint"] is not None:
                # We add a flat 9ft to the cloudbase calculation to account for the height of the sensor
                # We also add the field elevation of 363.2 meters
                self.output_data["cloudbase"] = round(cloudbase(self.output_data["outTemp"], self.output_data["dewpoint"]) + 2.7432 + 363.2, 1)

            # Initial rain, we can't calculate the rain rate
            if "rain_mm" in data and data["rain_mm"] is not None:
                if self.rain == -1:
                    self.output_data["rain"] = 0
                    self.rain = data["rain_mm"]
                # Rain has increased, calculate the rain rate
                elif self.rain < data["rain_mm"]:
                    self.output_data["rain"] = data["rain_mm"] - self.rain
                    self.rain = data["rain_mm"]
                # Rain has decreased, we had a reset
                elif self.rain > data["rain_mm"]:
                    self.output_data["rain"] = 0
                    self.rain = data["rain_mm"]
                # No change in rain, no rain
                else:
                    self.output_data["rain"] = 0
        elif message.topic == self.input_topic_indoor:
            # The indoor unit sometimes reports a negative temperature
            # The indoor unit sometimes reports a humidity much lower than the previous reading
            # Ignore these values
            if data["temperature"] < 0 or data["temperature"] > 50 or data["humidity"] < 0 or data["humidity"] > 100:
                return

            self.output_data["inTemp"] = round(data["temperature"], 1)
            self.output_data["inHumidity"] = data["humidity"]
            if "tvoc" in data and data["tvoc"] is not None:
                self.output_data["tvoc"] = round(data["tvoc"] * 0.001, 4)

            self.output_data["rain"] = 0

        elif message.topic == self.input_topic_particle_sensor:
            if "pm10" in data and data["pm10"] is not None:
                self.output_data["pm1_0"] = round(data["pm10"], 2)
            if "pm25" in data and data["pm25"] is not None:
                self.output_data["pm2_5"] = round(data["pm25"], 2)

            self.output_data["rain"] = 0

        elif message.topic == self.input_topic_lightning:
            if "presence" in data and data["presence"] is False:
                if "lightning_energy" in self.output_data:
                    self.output_data.pop("lightning_energy")
                if "lightning_distance" in self.output_data:
                    self.output_data.pop("lightning_distance")
                return
            if self.total_lightning_strikes == -1:
                self.total_lightning_strikes = 0
            self.total_lightning_strikes += 1
            self.output_data["lightning_strike_count"] = self.total_lightning_strikes
            self.client.publish(TOPIC_LIGHTNING_COUNT, str(self.total_lightning_strikes), retain=True)
            if "energy" in data and data["energy"] is not None:
                self.output_data["lightning_energy"] = data["energy"]
                # The AS3935 sensor reports the distance at arbitrary km intervals
                # Fix that by using the energy value to calculate the distance
                self.output_data["lightning_distance"] = round(2100 / math.sqrt(data["energy"]), 1)
            self.output_data["rain"] = 0

        elif message.topic == self.input_topic_light:
            if "lux" in data and data["lux"] is not None:
                self.output_data["luminosity"] = data["lux"]
            self.output_data["rain"] = 0

        elif message.topic == self.input_topic_pressure:
            # self.output_data["outTemp"] = round(data["temperature"], 1)
            if "pressure" in data and data["pressure"] is not None:
                self.output_data["barometer"] = round(data["pressure"], 2)
            self.output_data["rain"] = 0

        elif message.topic == self.input_topic_co2:
            if "co2" in data and data["co2"] is not None:
                self.output_data["co2"] = data["co2"]

        if self.sanity_check(self.output_data, self.previous_output_data):
            self.output_data["dateTime"] = time.mktime(datetime.now().astimezone().timetuple())
            # Publish the updated output data as a JSON string on the output topic
            client.publish(self.output_topic, json.dumps(self.output_data))

    def sanity_check(self, data, prev_data):
        # Check that the values are within the expected range
        if "outTemp" in data and (data["outTemp"] < -50 or data["outTemp"] > 150 or abs(data["outTemp"]-data["outTemp"]) > 30):
            return False
        if "outHumidity" in data and (data["outHumidity"] < 0 or data["outHumidity"] > 100 or abs(data["outHumidity"]-data["outHumidity"]) > 30):
            return False
        if "windDir" in data and (data["windDir"] < 0 or data["windDir"] > 360):
            return False
        if "windSpeed" in data and (data["windSpeed"] < 0 or data["windSpeed"] > 200):
            return False
        if "windGust" in data and (data["windGust"] < 0 or data["windGust"] > 200):
            return False
        if "heatindex" in data and (data["heatindex"] < -50 or data["heatindex"] > 150):
            return False
        if "windchill" in data and (data["windchill"] < -50 or data["windchill"] > 150):
            return False
        if "dewpoint" in data and (data["dewpoint"] < -50 or data["dewpoint"] > 150):
            return False
        if "frostpoint" in data and (data["frostpoint"] < -50 or data["frostpoint"] > 150):
            return False
        if "inTemp" in data and (data["inTemp"] < -50 or data["inTemp"] > 150 or abs(data["inTemp"]-data["inTemp"]) > 30):
            return False
        if "inHumidity" in data and (data["inHumidity"] < 0 or data["inHumidity"] > 100 or abs(data["inHumidity"]-data["inHumidity"]) > 30):
            return False
        return True

    # Define the on_connect function for the MQTT client
    def on_connect(self, client, userdata, flags, reason_code, properties):
        print("Connected with result code "+str(reason_code))
        # Subscribe to the input topics
        client.subscribe(TOPIC_LIGHTNING_COUNT)
        client.subscribe(self.input_topic_weather)
        client.subscribe(self.input_topic_indoor)
        client.subscribe(self.input_topic_lightning)
        client.subscribe(self.input_topic_light)
        client.subscribe(self.input_topic_pressure)
        client.subscribe(self.input_topic_particle_sensor)

    # Define the on_disconnect function for the MQTT client
    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            raise Exception("MQTT disconnection")
