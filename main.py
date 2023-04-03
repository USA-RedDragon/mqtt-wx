import argparse
import signal

from mqtt import MQTTClient


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("mqtt_host", help="MQTT host")
        parser.add_argument("mqtt_username", help="MQTT username")
        parser.add_argument("mqtt_password", help="MQTT password")
        parser.add_argument("input_topic_weather", help="Input topic for weather station data")
        parser.add_argument("input_topic_indoor", help="Input topic for indoor sensor data")
        parser.add_argument("input_topic_lightning", help="Input topic for lightning data")
        parser.add_argument("input_topic_light", help="Input topic for light data")
        parser.add_argument("input_topic_pressure", help="Input topic for pressure data")
        parser.add_argument("input_topic_particle_sensor", help="Input topic for particle sensor data")
        parser.add_argument("output_topic", help="Output topic for processed data")
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
        print(f"Unhandled error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
