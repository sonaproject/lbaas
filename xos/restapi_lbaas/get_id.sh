#!/bin/bash
#DB_CMD="docker exec -it sona_xos_db_1 psql -U postgres -d xos -P pager=off -x -c"
DB_CMD="docker exec -it sona_xos_db_1 psql -U postgres -d xos -P pager=off -c"

echo "[Loadbalancer]"
RESULT=`$DB_CMD "select tenantwithcontainer_ptr_id, loadbalancer_id, provisioning_status from lbaas_loadbalancer"`
echo "$RESULT"

echo "[Listener]"
RESULT=`$DB_CMD "select id, listener_id from lbaas_listener"`
echo "$RESULT"

echo "[Pool]"
RESULT=`$DB_CMD "select id, pool_id from lbaas_pool"`
echo "$RESULT"

echo "[Member]"
RESULT=`$DB_CMD "select id, ptr_pool_id, member_id from lbaas_member"`
echo "$RESULT"

echo "[Healthmonitor]"
RESULT=`$DB_CMD "select id, health_monitor_id from lbaas_healthmonitor"`
echo "$RESULT"

