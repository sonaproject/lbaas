#!/bin/bash
PROC1="python lbaas-synchronizer.py"
PROC2="python sync_config.py"

$PROC1 &
$PROC2 &

sleep 60

while :
do
    RESULT=`ps -ef | grep "$PROC1" | grep -v 'grep'`
    if [ "${RESULT:-null}" = null ]; then
        echo "${PROC1} not running, starting "$PROC1
        $PROC1 &
    else
        echo "${PROC1} running"
    fi

    RESULT=`ps -ef | grep "$PROC2" | grep -v 'grep'`
    if [ "${RESULT:-null}" = null ]; then
        echo "${PROC2} not running, starting "$PROC2
        $PROC2 &
    else
        echo "${PROC2} running"
    fi

    sleep 10
done
