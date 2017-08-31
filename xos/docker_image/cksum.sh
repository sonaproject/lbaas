#!/bin/sh

OLD_CKSUM=""
CUR_CKSUM=""
cksum /usr/local/etc/haproxy/haproxy.cfg

if [ $? != 0 ]
then
    sleep 60
    pkill cksum.sh
fi

while :
do
    CUR_CKSUM=`cksum /usr/local/etc/haproxy/haproxy.cfg | awk '{print $1}'`

    if [ "$CUR_CKSUM" != "$OLD_CKSUM" ] && [ "$OLD_CKSUM" != "" ]
    then
        service haproxy reload
        echo "`date`   Current CKSUM: $CUR_CKSUM    Old CKSUM: $OLD_CKSUM" >> /cksum.log
    fi

    sleep 2
    OLD_CKSUM=$CUR_CKSUM
done
