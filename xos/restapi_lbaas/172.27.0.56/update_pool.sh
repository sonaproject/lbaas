#!/bin/bash

source ./config.sh

if [[ "$#" -ne 2 ]]; then
    echo "Syntax: $0 <pool_id> <health_monitor_id>"
    exit -1
fi

POOL_ID=$1
HEALTH_ID=$2

DATA=$(cat <<EOF
{
    "ptr_health_monitor_id": "$HEALTH_ID",
    "lb_algorithm": "ROUND_ROBIN"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/pools/$POOL_ID/
