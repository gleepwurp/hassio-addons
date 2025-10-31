#!/usr/bin/env python3

import os
import sys
import json
import time
import logging
from typing import Dict, List
import paho.mqtt.client as mqtt
from prometheus_client import start_http_server, Gauge
from influx_parser import InfluxLineParser

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self, config: dict):
        """Initialize the metrics collector"""
        self.config = config
        self.mqtt_config = config['mqtt']
        self.servers = config['servers']
        self.metrics: Dict[str, Dict[str, Gauge]] = {}
        self.client = None
        self.setup_mqtt()
        self.setup_metrics()

    def setup_metrics(self):
        """Initialize Prometheus metrics for each server and area"""
        for server in self.servers:
            hostname = server['hostname']
            friendly_name = server['friendly_name']
            self.metrics[hostname] = {}

            # Pre-create some common metrics that we expect to see
            common_metrics = {
                'cpu': ['usage_user', 'usage_system', 'usage_idle'],
                'memory': ['used_percent', 'available', 'total'],
                'disk': ['used_percent', 'free', 'total'],
                'network': ['bytes_sent', 'bytes_recv']
            }

            for area in server['areas']:
                # Initialize with common metrics if we know them
                if area in common_metrics:
                    for metric in common_metrics[area]:
                        metric_name = f"telegraf_{area}_{metric}"
                        self.metrics[hostname][f"{area}_{metric}"] = Gauge(
                            metric_name,
                            f"Telegraf {area} {metric} metric",
                            ['host', 'friendly_name']
                        )

    def setup_mqtt(self):
        """Set up MQTT client and connection"""
        self.client = mqtt.Client(self.mqtt_config.get('client_id', 'telegraf-metrics-addon'))

        if self.mqtt_config.get('username'):
            self.client.username_pw_set(
                self.mqtt_config['username'],
                self.mqtt_config.get('password', '')
            )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(
                self.mqtt_config['broker'],
                self.mqtt_config.get('port', 1883),
                60
            )
        except Exception as err:
            logger.error(f"Failed to connect to MQTT broker: {err}")
            sys.exit(1)

    def on_connect(self, client, userdata, flags, rc):
        """Callback for when MQTT connection is established"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to all server topics
            for server in self.servers:
                topic = f"telegraf/{server['hostname']}/#"
                logger.info(f"Subscribing to {topic}")
                client.subscribe(topic)
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            # Parse topic to get hostname and area
            # Format: telegraf/hostname/area
            parts = msg.topic.split('/')
            if len(parts) != 3:
                return

            hostname = parts[1]
            area = parts[2]

            # Find server config
            server = next((s for s in self.servers if s['hostname'] == hostname), None)
            if not server:
                logger.warning(f"Received message for unknown host: {hostname}")
                return

            # Parse message payload using InfluxDB line protocol parser
            payload = msg.payload.decode('utf-8')
            for line in payload.splitlines():
                try:
                    measurement, tags, fields, timestamp = InfluxLineParser.parse_line(line)

                    # Update Prometheus metrics
                    for field_name, field_value in fields.items():
                        metric_key = f"{measurement}_{field_name}"

                        # Create metric if it doesn't exist
                        if metric_key not in self.metrics[hostname]:
                            self.metrics[hostname][metric_key] = Gauge(
                                f"telegraf_{measurement}_{field_name}",
                                f"Telegraf {measurement} {field_name} metric",
                                ['host', 'friendly_name'] + list(tags.keys())
                            )

                        # Set metric value with all labels
                        labels = {
                            'host': hostname,
                            'friendly_name': server['friendly_name'],
                            **tags
                        }
                        self.metrics[hostname][metric_key].labels(**labels).set(field_value)

                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error parsing line '{line}': {e}")
                    continue

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def run(self):
        """Start the metrics collector"""
        # Start Prometheus HTTP server
        start_http_server(9100)

        # Start MQTT loop
        self.client.loop_start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()

def set_log_level(level_str: str):
    """Set log level based on string input"""
    levels = {
        'trace': logging.DEBUG,  # No TRACE in Python logging
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'notice': logging.INFO,  # No NOTICE in Python logging
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'fatal': logging.CRITICAL
    }
    logger.setLevel(levels.get(level_str.lower(), logging.INFO))

def main():
    """Main entry point"""
    # Load configuration
    if not os.path.exists('/data/options.json'):
        logger.error("No configuration file found")
        sys.exit(1)

    with open('/data/options.json', 'r') as f:
        config = json.load(f)

    # Set log level
    set_log_level(config.get('log_level', 'info'))

    # Start collector
    collector = MetricsCollector(config)
    collector.run()

if __name__ == "__main__":
    main()