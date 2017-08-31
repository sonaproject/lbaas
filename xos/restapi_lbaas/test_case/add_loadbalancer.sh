#!/bin/bash

source ./config.sh

DATA=$(cat <<EOF
{
    "name": "sona_loadbalancer",
    "slice_name": "mysite_net-a",
    "description": "web server loadbalancer"
}
EOF
) 

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/loadbalancers/
