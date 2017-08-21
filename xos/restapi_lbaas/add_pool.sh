#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: $0 <health_monitor_id>"
    exit -1
fi

HEALTH_ID=$1

DATA=$(cat <<EOF
{
    "name": "sona_pool",
    "health_monitor_id": "$HEALTH_ID",
    "lb_algorithm": "ROUND_ROBIN",
    "protocol": "HTTP",
    "description": "sona_pool"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/pools/
