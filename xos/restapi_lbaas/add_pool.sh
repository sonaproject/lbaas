#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    #echo "Syntax: $0"

DATA=$(cat <<EOF
{
    "name": "sona_pool",
    "lb_algorithm": "ROUND_ROBIN",
    "protocol": "HTTP",
    "description": "sona_pool"
}
EOF
)

else
    #echo "Syntax: $0 <health_monitor_id>"
    HEALTH_ID=$1

DATA=$(cat <<EOF
{
    "name": "sona_pool",
    "ptr_health_monitor_id": "$HEALTH_ID",
    "lb_algorithm": "ROUND_ROBIN",
    "protocol": "HTTP",
    "description": "sona_pool"
}
EOF
)

fi
curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/pools/
