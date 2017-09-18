#!/bin/sh
set -e

CFG_FILE="/usr/local/etc/haproxy/haproxy.cfg"

# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]; then
        set -- haproxy "$@"
fi

if [ "$1" = 'haproxy' ]; then
        # if the user wants "haproxy", let's use "haproxy-systemd-wrapper" instead so we can have proper reloadability implemented by upstream
        shift # "haproxy"
        set -- "$(which haproxy-systemd-wrapper)" -p /run/haproxy.pid "$@"
fi

while [ ! -f "$CFG_FILE" ]:
do
    echo "`date` Not found $CFG_FILE" >> /cksum.log
    sleep 2
done

echo "`date` Found $CFG_FILE" >> /cksum.log
/cksum.sh &
exec "$@"
