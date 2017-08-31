#!/bin/bash

source ./config.sh

DATA=$(cat <<EOF
{
    "name": "sona_listener",
    "protocol": "HTTP",
    "protocol_port": 10001,
    "stat_port": 10002,
    "description": "sona_listener"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/listeners/
