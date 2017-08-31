#!/bin/bash

source ./config.sh

if [[ "$#" -ne 2 ]]; then
    echo "Syntax: $0 <pool_id> <member_id>"
    exit -1
fi

POOL_ID=$1
MEMBER_ID=$2

DATA=$(cat <<EOF
{
    "address": "10.10.2.200",
    "protocol_port": 8888
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/pools/$POOL_ID/members/$MEMBER_ID/
