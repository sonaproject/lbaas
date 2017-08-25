#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: $0 <listener_id>"
    exit -1
fi

LISTENER_ID=$1

DATA=$(cat <<EOF
{
    "protocol": "HTTP",
    "protocol_port": 20001,
    "stat_port": 20002
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/listeners/$LISTENER_ID/

