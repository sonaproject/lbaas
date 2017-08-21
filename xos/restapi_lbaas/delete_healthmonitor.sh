#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: $0 <healthmonitor_id>"
    exit -1
fi

HEALTH_ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X DELETE $HOST/api/tenant/healthmonitors/$HEALTH_ID/ -v
