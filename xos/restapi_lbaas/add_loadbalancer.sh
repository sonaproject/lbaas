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
    "vip_address": "0.0.0.0",
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
    "vip_address": "0.0.0.0",
    "description": "web server loadbalancer"
}
EOF
) 

fi


<< "COMMENT"
DATA=$(cat <<EOF
{
    "name": "sona_loadbalancer",
    "vip_subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2",
    "vip_address": "10.6.1.198",
    "description": "web server loadbalancer100"
}
EOF
)
COMMENT

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/loadbalancers/
