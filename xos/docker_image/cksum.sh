#!/bin/sh
CFG_FILE="/usr/local/etc/haproxy/haproxy.cfg"
OLD_CKSUM=""
CUR_CKSUM=""

echo "`date` Start cksum.sh" >> /cksum.log

while :
do
    CUR_CKSUM=`cksum $CFG_FILE | awk '{print $1}'`

    if [ "$CUR_CKSUM" != "$OLD_CKSUM" ] && [ "$OLD_CKSUM" != "" ]
    then
        service haproxy reload
        echo "`date` Reload $CFG_FILE" >> /cksum.log
    fi

    sleep 2
    OLD_CKSUM=$CUR_CKSUM
done
