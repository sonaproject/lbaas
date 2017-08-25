#!/bin/sh


OLD_CKSUM=""
CUR_CKSUM=""
INIT_CKSUM=""
cksum /usr/local/etc/haproxy/haproxy.cfg

if [ $? != 0 ]
then
    INIT_CKSUM=`cksum /usr/local/etc/haproxy/haproxy.cfg`
fi

while :
do
    CUR_CKSUM=`cksum /usr/local/etc/haproxy/haproxy.cfg | awk '{print $1}'`

    echo "`date`   Current CKSUM: $CUR_CKSUM" >> /cksum.log

    if [ "$INIT_CKSUM" = "" ] && [ "$CUR_CKSUM" != "" ]
    then
        kill -HUP 1
        echo "`date`   Current CKSUM: $CUR_CKSUM    INIT_CKSUM: $INIT_CKSUM" >> /cksum.log
    fi


    if [ "$CUR_CKSUM" != "$OLD_CKSUM" ] && [ "$OLD_CKSUM" != "" ]
    then
        kill -HUP 1
        echo "`date`   Current CKSUM: $CUR_CKSUM    Old CKSUM: $OLD_CKSUM" >> /cksum.log
    fi

    sleep 2
    OLD_CKSUM=$CUR_CKSUM
done

