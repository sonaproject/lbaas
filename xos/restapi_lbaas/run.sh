./add_listener.sh
./add_healthmonitor.sh
./add_pool.sh 1
./add_member.sh 1 10.10.2.241 9001    # test web server: 10.10.2.241
./add_member.sh 1 10.10.2.242 9001    # test web server: 10.10.2.242
./add_loadbalancer.sh 1 1
