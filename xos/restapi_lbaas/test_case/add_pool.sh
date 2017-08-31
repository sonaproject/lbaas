#!/bin/bash

source ./config.sh

DATA=$(cat <<EOF
{
    "name": "sona_pool",
    "lb_algorithm": "ROUND_ROBIN",
    "protocol": "HTTP",
    "description": "sona_pool"
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/pools/
