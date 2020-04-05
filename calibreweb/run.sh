#!/usr/bin/with-contenv bashio

set -e
CONFIG_PATH=/data/options.json
SYSTEM_USER=/data/system_user.json

python /cw/cps.py -p /data/cw.db
