ARG BUILD_FROM=ghcr.io/hassio-addons/base/amd64:9.2.0
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Copy root filesystem
COPY rootfs /

# Setup base
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-paho-mqtt

RUN pip3 install \
    paho-mqtt \
    prometheus-client

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="Telegraf Metrics" \
    io.hass.description="Collect and process Telegraf metrics from MQTT topics" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Gleepwurp" \
    org.opencontainers.image.title="Telegraf Metrics" \
    org.opencontainers.image.description="Collect and process Telegraf metrics from MQTT" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}