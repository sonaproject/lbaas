#!/bin/bash

source ./config.sh

if [[ "$#" -ne 2 ]]; then
    echo "Syntax: $0 <pool_id> <HEALTH_ID>"
    exit -1
fi

POOL_ID=$1
HEALTH_ID=$2

DATA=$(cat <<EOF
{
    "health_monitor_id": null
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/pools/$POOL_ID/
