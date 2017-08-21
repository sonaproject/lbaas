import importlib
import os
import sys
import time
import threading
from xosconfig import Config
config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/lbaas_config.yaml')
Config.init(config_file, 'synchronizer-config-schema.yaml')

sys.path.insert(0, "/opt/xos")
from xos.logger import Logger, logging
from synchronizers.new_base.modelaccessor import *

logger = Logger(level=logging.INFO)


def update_lb_vip_addr(instance_id, vip_address):
    lb = Loadbalancer.objects.get(instance_id=instance_id)
    lb.vip_address = vip_address
    lb.save()

    for idx in range(1, 180, 1):
        time.sleep(1)
        ins = ServiceInstance.objects.get(id=instance_id)
        if ins.updated == ins.enacted:
            logger.info("[Thread] [%d] updated ServiceInstance" % idx)
            ins.updated = time.time()
            ins.save()

        ins = ServiceInstance.objects.get(id=instance_id)
        if ins.updated != ins.enacted:
            break;

    logger.info("[Thread] lb.vip_address = %s" % lb.vip_address)

def check_lb_vip_address():
    time.sleep(30)

    while True:
        time.sleep(10)

        lbs_list = []
        ports_list = []

        lbs = Loadbalancer.objects.all()
        logger.info("[Thread] lbs.count = %s" % len(lbs))

        for lb in lbs:
            lb_info = {}
            lb_info['id'] = lb.id
            lb_info['instance_id'] = lb.id
            lb_info['vip_address'] = lb.vip_address
            logger.info("[Thread] [Loadbalancer] lb.id=%s, lb.instance_id=%s, lb.vip=%s" \
                % (lb.id, lb.instance_id, lb.vip_address))
            lbs_list.append(lb_info)

        if len(lbs) == 0:
            continue

        ports = Port.objects.filter(id=lbs[0].vip_subnet_id)
        logger.info("[Thread] ports.count = %s" % len(ports))

        for port in ports:
            port_info = {}
            port_info['instance_id'] = port.instance_id
            port_info['ip'] = port.ip
            logger.info("[Thread] [Port] port.instance_id=%s, port.ip=%s" % (port.instance_id, port.ip))
            ports_list.append(port_info)

        for lb in lbs_list:
            for port in ports_list:
                if lb['instance_id'] == port['instance_id'] and lb['vip_address'] != port['ip']:
                    logger.info("[Thread] instance_id=%s, lb.vip_address=%s, port.ip=%s" \
                        % (lb['instance_id'], lb['vip_address'], port['ip']))

                    update_lb_vip_addr(lb['instance_id'], port['ip'])


if __name__ == "__main__":
    lb_thr = threading.Thread(target=check_lb_vip_address)
    lb_thr.start()
