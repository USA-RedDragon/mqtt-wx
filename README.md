# mqtt-wx

This is a little translation layer between rtl_443 and Home Assistant + WeeWX for a Cotech 36-7959 Weatherstation or other compatible models. Specifically, this is intended to take in two MQTT topics (one for the weather station itself and the other for the indoor module) and coalesce them into a single topic.

For WeeWX, this uses <https://github.com/USA-RedDragon/weewxMQTT> to read weather data from MQTT. An example `weewx.conf` entry can be found in `examples/weewx.conf`

A Home Assistant example config can be found in `examples/home_assistant.yaml`.

This project is a single-purpose project and does not accept bug reports or most PRs.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/USA-RedDragon
    ```

1. Install the required packages by running:

   ```bash
   pip install -r requirements.txt
   ```

1. A systemd service unit file example has been included at `examples/mqtt-wx.service`. Be sure to replace the content of the `ExecStart` line with the appropriate path to `mqtt-wx` and arguments.

## Usage

Run the program by executing the following command:

```bash
python mqtt-wx.py \
  <mqtt_host> \
  <mqtt_username> \
  <mqtt_password> \
  <input_topic_weather> \
  <input_topic_indoor> \
  <output_topic>
```

Make sure to replace the placeholders with the appropriate values for your MQTT broker and topics.

### Command line arguments

The following command line arguments are available:

- `mqtt_host`: the hostname or IP address of the MQTT broker
- `mqtt_username`: the username for the MQTT broker
- `mqtt_password`: the password for the MQTT broker
- `input_topic_weather`: the topic for the weather station data
- `input_topic_indoor`: the topic for the indoor sensor data
- `output_topic`: the topic to publish the output data to
