#!/usr/bin/env python3

from typing import Dict, Optional, Tuple

class InfluxLineParser:
    @staticmethod
    def parse_line(line: str) -> Tuple[str, Dict[str, str], Dict[str, float], Optional[int]]:
        """Parse an InfluxDB line protocol line

        Args:
            line (str): Line in InfluxDB line protocol format

        Returns:
            Tuple containing:
            - measurement name (str)
            - tags (Dict[str, str])
            - fields (Dict[str, float])
            - timestamp (Optional[int])
        """
        # Split into measurement+tags, fields, and timestamp
        parts = line.strip().split(' ')
        if len(parts) < 2:
            raise ValueError("Invalid line format")

        measurement_tags = parts[0]
        fields = parts[1]
        timestamp = int(parts[2]) if len(parts) > 2 else None

        # Parse measurement and tags
        measurement_parts = measurement_tags.split(',')
        measurement = measurement_parts[0]
        tags = {}
        if len(measurement_parts) > 1:
            for tag in measurement_parts[1:]:
                key, value = tag.split('=')
                tags[key] = value.strip('"')

        # Parse fields
        fields_dict = {}
        for field in fields.split(','):
            key, value = field.split('=')
            # Handle different value types
            value = value.strip('"')
            try:
                if value.endswith('i'):  # Integer
                    fields_dict[key] = float(value[:-1])
                elif value.lower() == 'true':
                    fields_dict[key] = 1.0
                elif value.lower() == 'false':
                    fields_dict[key] = 0.0
                else:
                    fields_dict[key] = float(value)
            except ValueError:
                continue  # Skip fields that can't be converted to float

        return measurement, tags, fields_dict, timestamp