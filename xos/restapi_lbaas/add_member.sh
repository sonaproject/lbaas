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
    "memberpool": "$POOL_ID",
    "address": "$MEMBER_IP",
    "protocol_port": $PORT
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/pools/$POOL_ID/members/
