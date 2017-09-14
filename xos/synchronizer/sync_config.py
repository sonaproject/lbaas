import importlib
import os
import sys
import time
import datetime
import threading
import json

from xosconfig import Config
config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/lbaas_config.yaml')
Config.init(config_file, 'synchronizer-config-schema.yaml')

sys.path.insert(0, "/opt/xos")
from synchronizers.new_base.modelaccessor import *
import lbaas_log as slog

def update_lb_vip_addr(instance_id, vip_address):
    try:
        lb = Loadbalancer.objects.get(instance_id=instance_id)
        lb.vip_address = vip_address
        lb.save()
    except Exception as err:
        slog.error("%s" % str(err))

    try:
        config = LBconfig.objects.get(instance_id=instance_id)
        config.ansible_update=True
        config.save()
    except Exception as err:
        slog.error("%s" % str(err))

    for idx in range(1, 180, 1):
        config = LBconfig.objects.get(instance_id=instance_id)
        if config.ansible_update:
            ins = ServiceInstance.objects.get(id=instance_id)
            if ins.updated <= ins.enacted:
                ins.updated = time.time()
                slog.info("[idx=%s] update time(%s) of instance_id(%s)" % (idx, ins.updated, lb.instance_id))
                ins.save()
            else:
                break

            time.sleep(1)

    slog.info("[Thread] lb.vip_address = %s" % lb.vip_address)

def check_lb_vip_address():
    while True:
        time.sleep(5)
        lbs_list = []
        ports_list = []

        lbs = Loadbalancer.objects.all()
        slog.info("[Thread] lbs.count = %s" % len(lbs))

        for lb in lbs:
            lb_info = {}
            lb_info['id'] = lb.id
            lb_info['instance_id'] = lb.id
            lb_info['vip_address'] = lb.vip_address
            slog.info("[Thread] [Loadbalancer] lb.id=%s, lb.instance_id=%s, lb.vip=%s" \
                % (lb.id, lb.instance_id, lb.vip_address))
            lbs_list.append(lb_info)

        if len(lbs) == 0:
            continue

        ports = Port.objects.all()
        slog.info("[Thread] ports.count = %s" % len(ports))

        for port in ports:
            port_info = {}
            port_info['instance_id'] = port.instance_id
            port_info['ip'] = port.ip
            slog.info("[Thread] [Port] port.instance_id=%s, port.ip=%s" % (port.instance_id, port.ip))
            ports_list.append(port_info)

        for lb in lbs_list:
            for port in ports_list:
                if lb['instance_id'] == port['instance_id'] and lb['vip_address'] != port['ip']:
                    slog.info("[Thread] instance_id=%s, lb.vip_address=%s, port.ip=%s" \
                        % (lb['instance_id'], lb['vip_address'], port['ip']))

                    update_lb_vip_addr(lb['instance_id'], port['ip'])

def check_instance_status():
    while True:
        time.sleep(5)
        instances = Instance.objects.all()
        slog.info("[Thread] instances.count = %s" % len(instances))

        for ins in instances:
            tag=""
            provisioning_status=""

            try:
                tag = Tag.objects.get(object_id=ins.id, name="chk_container_status")
            except Exception as err:
                slog.error("[Thread] Error: object_id(%s) does not exist in Tag table (%s)" % (ins.id, str(err)))
                continue

            if ins.backend_code == 0:
                provisioning_status="PENDING_UPDATE"

            elif ins.backend_code == 1:
                if tag.value == "":
                    provisioning_status="PENDING_UPDATE"
                else:
                    try:
                        userData = json.loads(tag.value)
                        create_timestamp = time.mktime(datetime.datetime.strptime(userData['create_date'], "%Y-%m-%d %H:%M:%S").timetuple())
                        update_timestamp = time.mktime(datetime.datetime.strptime(userData['update_date'], "%Y-%m-%d %H:%M:%S").timetuple())
                        
                        if userData['result'] == "Initialized":
                            provisioning_status="PENDING_UPDATE"
                        elif userData['expected_result'] != userData['result'] and (float(update_timestamp)-float(create_timestamp)) > 30:
                            provisioning_status="ERROR"
                        else:
                            provisioning_status="ACTIVE"
                    except Exception as err:
                        slog.error("[Thread] Error: json.loads() failed (%s)" % str(err))
            else:
                try:
                    userData = json.loads(tag.value)
                    create_timestamp = time.mktime(datetime.datetime.strptime(userData['create_date'], "%Y-%m-%d %H:%M:%S").timetuple())
                    update_timestamp = time.mktime(datetime.datetime.strptime(userData['update_date'], "%Y-%m-%d %H:%M:%S").timetuple())
                        
                    if (float(update_timestamp)-float(create_timestamp)) < 30:
                        provisioning_status="PENDING_UPDATE"
                    else:
                        provisioning_status="ERROR"
                except Exception as err:
                        slog.error("[Thread] Error: json.loads() failed (%s)" % str(err))               

            try:
                lb = Loadbalancer.objects.get(tenantwithcontainer_ptr_id=ins.id)
                lb.provisioning_status = provisioning_status
                lb.save()
                slog.info("[Thread] id=%s, instance_name=%s, lb.provisioning_status=%s" 
                    % (ins.id, ins.instance_name, lb.provisioning_status))
            except Exception as err:
                slog.error("[Thread] Error: id(%s) does not exist in Loadbalancer table (%s)" % (ins.id, str(err)))



if __name__ == "__main__":
    models_active = False
    wait = False

    while not models_active:
        try:
            first_controller = Controller.objects.first()
            slog.debug("one of controller set: %s" % first_controller.name) 
            first_image      = Image.objects.first()
            slog.debug("one of image set     : %s" % first_image.name) 
            models_active = True 
        except Exception,e:
            slog.info(str(e))
            slog.info('Waiting for data model to come up before starting...')
            time.sleep(3)
            wait = True

    slog.debug("Data Model is active (first_controller: %s)" % first_controller)

    if (wait):
        time.sleep(5) # Safety factor, seeing that we stumbled waiting for the data model to come up.

    lb_thr = threading.Thread(target=check_lb_vip_address)
    lb_thr.start()

    ins_thr = threading.Thread(target=check_instance_status)
    ins_thr.start()
