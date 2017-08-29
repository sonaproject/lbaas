#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: $0 <health_monitor_id>"
    exit -1
fi

HEALTH_ID=$1

DATA=$(cat <<EOF
{
    "ptr_health_monitor_id": "$HEALTH_ID",
    "delay": 7,
    "max_retries": 7,
    "timeout": 7
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/healthmonitors/$HEALTH_ID/
