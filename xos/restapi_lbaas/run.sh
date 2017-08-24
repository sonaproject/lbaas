#!/bin/bash
DB_CMD="docker exec -it sona_xos_db_1 psql -U postgres -d xos -P pager=off -x -c"

######################################################
# delete lb model info
######################################################
$DB_CMD "delete from lbaas_loadbalancer"
$DB_CMD "delete from lbaas_listener"
$DB_CMD "delete from lbaas_member"
$DB_CMD "delete from lbaas_pool"
$DB_CMD "delete from lbaas_healthmonitor"

######################################################
# create lb model info
######################################################
./add_listener.sh 
./add_healthmonitor.sh 

# get health_monitor_id
RESULT=`$DB_CMD "select * from lbaas_healthmonitor limit 1" | grep health_monitor_id`
HEALTH_ID=`echo ${RESULT::-1} | awk '{print $3}'`
./add_pool.sh $HEALTH_ID

# get pool_id
RESULT=`$DB_CMD "select * from lbaas_pool limit 1" | grep pool_id`
POOL_ID=`echo ${RESULT::-1} | awk '{print $3}'`
./add_member.sh $POOL_ID 10.10.2.241 9001
./add_member.sh $POOL_ID 10.10.2.242 9001

# get listener_id
RESULT=`$DB_CMD "select * from lbaas_listener limit 1" | grep listener_id`
LISTENER_ID=`echo ${RESULT::-1} | awk '{print $3}'`
./add_loadbalancer.sh $LISTENER_ID $POOL_ID
