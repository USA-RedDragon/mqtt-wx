import argparse
import signal
import sys
import traceback

from mqtt import MQTTClient
from config import get_config


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-mqtt_host", help="MQTT host", default=get_config().mqtt_host, required=False)
        parser.add_argument("-mqtt_username", help="MQTT username", default=get_config().mqtt_username, required=False)
        parser.add_argument("-mqtt_password", help="MQTT password", default=get_config().mqtt_password, required=False)
        parser.add_argument("-input_topic_weather", help="Input topic for weather station data", default=get_config().input_topic_weather, required=False)
        parser.add_argument("-input_topic_indoor", help="Input topic for indoor sensor data", default=get_config().input_topic_indoor, required=False)
        parser.add_argument("-input_topic_lightning", help="Input topic for lightning data", default=get_config().input_topic_lightning, required=False)
        parser.add_argument("-input_topic_light", help="Input topic for light data", default=get_config().input_topic_light, required=False)
        parser.add_argument("-input_topic_pressure", help="Input topic for pressure data", default=get_config().input_topic_pressure, required=False)
        parser.add_argument("-input_topic_particle_sensor", help="Input topic for particle sensor data", default=get_config().input_topic_particle_sensor, required=False)
        parser.add_argument("-output_topic", help="Output topic for processed data", default=get_config().output_topic, required=False)
        args = parser.parse_args()

        def signal_handler(sig, frame):
            client.stop()
            exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        client = MQTTClient(
            args.mqtt_host,
            args.mqtt_username,
            args.mqtt_password,
            args.input_topic_weather,
            args.input_topic_indoor,
            args.input_topic_lightning,
            args.input_topic_light,
            args.input_topic_pressure,
            args.input_topic_particle_sensor,
            args.output_topic
        )

        client.start()
    except Exception as e:
        print(e)
        traceback.print_exception(*sys.exc_info())
        exit(1)


if __name__ == "__main__":
    main()
