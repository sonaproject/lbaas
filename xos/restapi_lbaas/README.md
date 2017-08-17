You can follow below commands:

# 사전작업
아래 명령을 수행하여 XOS Core의 service 정보를 생성한다. 
```
docker exec sona_xos_ui_1 python tosca/run.py xosadmin@opencord.org /opt/cord_profile/swarm-node.yaml; pushd /root/cord/build/platform-install; ansible-playbook -i inventory/sona onboard-lbaas-playbook.yml; popd
```

# 절차 A 
```
add_listener.sh
add_healthmonitor.sh
add_pool.sh 1
add_member.sh 1 10.10.2.241 9001    # test web server: 10.10.2.241
add_member.sh 1 10.10.2.242 9001    # test web server: 10.10.2.242
add_loadbalancer.sh 1 1
```

# 절차 B
This is like a openstack flow 
```
add_loadbalancer.sh  
add_listener.sh
add_healthmonitor.sh
add_pool.sh 1
add_member.sh 1 10.10.2.241 9001    # test web server: 10.10.2.241
add_member.sh 1 10.10.2.242 9001    # test web server: 10.10.2.242
update_loadbalancer.sh  f7b8129b-75c6-4dc9-8ec9-a445b6ecda65  1  1
```
