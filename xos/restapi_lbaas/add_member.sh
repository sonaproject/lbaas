#!/bin/bash

source ./config.sh

if [[ "$#" -ne 3 ]]; then
    echo "Syntax: $0 <pool_id> <member_ip> <port>"
    exit -1
fi

POOL_ID=$1
MEMBER_IP=$2
PORT=$3

DATA=$(cat <<EOF
{
    "provider_service": 9,
    "memberpool": "$POOL_ID",
    "address": "$MEMBER_IP",
    "protocol_port": $PORT,
    "subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/pools/$POOL_ID/members/
