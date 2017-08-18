#!/bin/bash

source ./config.sh

DATA=""

if [[ "$#" -ne 2 ]]; then
    echo "Syntax: $0 <listener_id> <pool_id>"
    echo "====================================="
    #exit -1

DATA=$(cat <<EOF
{
    "name": "sona_loadbalancer",
    "vip_subnet_id": 1,
    "description": "web server loadbalancer"
}
EOF
) 

else 

    LISTENER_ID=$1
    POOL_ID=$2

DATA=$(cat <<EOF
{
    "name": "sona_loadbalancer",
    "listener": "$LISTENER_ID",
    "pool": "$POOL_ID",
    "vip_subnet_id": 1,
    "description": "web server loadbalancer"
}
EOF
) 

fi

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/loadbalancers/
