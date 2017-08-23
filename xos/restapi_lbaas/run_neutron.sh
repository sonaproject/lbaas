./add_loadbalancer.sh
./add_listener.sh
./add_pool.sh
./add_healthmonitor.sh
./update_pool.sh d0310527-5682-416d-b89d-741166a0f69d 1
./add_member.sh 1 10.10.2.241 9001    # test web server: 10.10.2.241
./add_member.sh 1 10.10.2.242 9001    # test web server: 10.10.2.242
./update_loadbalancer.sh  f7b8129b-75c6-4dc9-8ec9-a445b6ecda65  2  2
