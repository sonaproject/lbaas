#!/bin/bash

source ./config.sh

DATA=""

if [[ "$#" -ne 2 ]]; then
   # echo "Syntax: $0"

DATA=$(cat <<EOF
{
    "name": "sona_loadbalancer",
    "slice_name": "mysite_net-a",
    "description": "web server loadbalancer"
}
EOF
) 

else 
    #echo "Syntax: $0 <listener_id> <pool_id>"

    LISTENER_ID=$1
    POOL_ID=$2

DATA=$(cat <<EOF
{
    "name": "sona_loadbalancer",
    "ptr_listener_id": "$LISTENER_ID",
    "ptr_pool_id": "$POOL_ID",
    "slice_name": "mysite_net-a",
    "description": "web server loadbalancer"
}
EOF
) 

fi

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/loadbalancers/
