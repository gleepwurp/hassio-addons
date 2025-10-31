# Home Assistant Add-on: Telegraf Metrics

Collect and process Telegraf metrics from MQTT topics.

## About

This add-on subscribes to Telegraf metrics published to MQTT topics and makes them available as Prometheus metrics. It supports multiple servers and organizes metrics by areas (cpu, memory, disk, network, etc.).

## Configuration

Example configuration:

```yaml
mqtt:
  broker: core-mosquitto
  port: 1883
  username: mqtt_user
  password: mqtt_password
  client_id: telegraf-metrics-addon
servers:
  - hostname: server1
    friendly_name: Main Server
    areas:
      - cpu
      - memory
      - disk
      - network
  - hostname: server2
    friendly_name: Backup Server
    areas:
      - cpu
      - memory
update_interval: 60
log_level: info
```

### Option: `mqtt`

MQTT broker configuration:
- `broker`: Hostname of the MQTT broker (default: core-mosquitto)
- `port`: Port of the MQTT broker (default: 1883)
- `username`: Username for MQTT authentication (optional)
- `password`: Password for MQTT authentication (optional)
- `client_id`: MQTT client ID (optional)

### Option: `servers`

List of servers to monitor:
- `hostname`: Server hostname used in MQTT topic (/telegraf/hostname/*)
- `friendly_name`: Human-readable name for the server
- `areas`: List of metric areas to collect (cpu, memory, disk, network, etc.)

### Option: `update_interval`

Interval in seconds between metric updates (10-3600).

### Option: `log_level`

Log level: trace, debug, info, notice, warning, error, fatal.

## MQTT Topic Format

Metrics should be published to MQTT topics in this format:
```
telegraf/hostname/area
```

With payload in InfluxDB line protocol format:
```
measurement[,tag_key=tag_value...] field_key=field_value[,field_key2=field_value2...] [timestamp]
```

Example:
```
telegraf/server1/cpu
cpu,cpu=cpu0 usage_user=2.5,usage_system=1.8,usage_idle=95.7 1635683462000000000
cpu,cpu=cpu1 usage_user=3.1,usage_system=2.0,usage_idle=94.9 1635683462000000000
```

## Metrics

The add-on exposes metrics on port 9100 in Prometheus format. Each metric is labeled with:
- `host`: Server hostname
- `friendly_name`: Server's friendly name

Common metrics are automatically created for known areas:
- CPU: usage_user, usage_system, usage_idle
- Memory: used_percent, available, total
- Disk: used_percent, free, total
- Network: bytes_sent, bytes_recv

Additional metrics are created dynamically as they are received.