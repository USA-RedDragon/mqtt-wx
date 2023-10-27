import os

class Config:
    def __init__(self):
        self.mqtt_host = os.environ.get("MQTT_HOST") or "localhost"
        self.mqtt_username = os.environ.get("MQTT_USERNAME") or ""
        self.mqtt_password = os.environ.get("MQTT_PASSWORD") or ""
        self.input_topic_weather = os.environ.get("INPUT_TOPIC_WEATHER") or "weather"
        self.input_topic_indoor = os.environ.get("INPUT_TOPIC_INDOOR") or "indoor"
        self.input_topic_lightning = os.environ.get("INPUT_TOPIC_LIGHTNING") or "lightning"
        self.input_topic_light = os.environ.get("INPUT_TOPIC_LIGHT") or "light"
        self.input_topic_pressure = os.environ.get("INPUT_TOPIC_PRESSURE") or "pressure"
        self.input_topic_particle_sensor = os.environ.get("INPUT_TOPIC_PARTICLE_SENSOR") or "particle_sensor"
        self.output_topic = os.environ.get("OUTPUT_TOPIC") or "processed"

_config = None
def get_config():
    global _config
    if _config is None:
        _config = Config()
    return _config
