from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from django.conf import settings
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

from xos.logger import Logger, logging
logger = Logger(level=logging.INFO)

from rest_framework.authentication import *

from services.lbaas.models import LbService, Loadbalancer, Listener, Pool, Member, Healthmonitor, LBconfig

import json
import uuid
import traceback
import time
import threading

settings.DEBUG = False

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

def get_default_lb_service():
    lb_services = LbService.objects.all()
    if lb_services:
        return lb_services[0]
    return None

def update_loadbalancer_model(listener_id):

    lbs = Loadbalancer.objects.filter(ptr_listener_id=listener_id)
    for lb in lbs:
        try:
            config = LBconfig.objects.get(instance_id=lb.instance.id)
            config.ansible_update=True
            config.save()
        except Exception as err:
            logger.error("%s" % str(err))

    for lb in lbs:
        for idx in range (1, 60, 1):
            config = LBconfig.objects.get(instance_id=lb.instance.id)
            if config.ansible_update:
                ins = ServiceInstance.objects.get(id=lb.instance_id)
                if ins.updated <= ins.enacted:
                    ins.updated = time.time()
                    logger.info("[idx=%s] update time(%s) of instance_id(%s)" % (idx, ins.updated, lb.instance_id))
                    ins.save()
            else:
                break

            time.sleep(1)

    if lbs.count() == 0:
        logger.info("ptr_listener_id(%s) does not exist in Loadbalancer table" % ptr_listener_id)

class ListenerSerializer(PlusModelSerializer):
    id = ReadOnlyField()

    class Meta:
        model = Listener
        fields = ('id', 'name', 'protocol', 'protocol_port', 'stat_port', 'admin_state_up', 'connection_limit', 'description')

class ListenerViewSet(XOSViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    base_name = "listeners"
    method_name = "listeners"
    method_kind = "viewset"
    queryset = Listener.objects.all()
    serializer_class = ListenerSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ListenerViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def print_message_log(self, msg_type, http):
        if msg_type == "REQ":
            logger.info("###################################################")
            logger.info("[Server] <--- Client]")
            logger.info("METHOD=%s" % http.method)
            logger.info("URI=%s" % http.path)
            logger.info("%s\n" % http.data)
        elif msg_type == "RSP":
            logger.info("[Server] ---> [Client]")
            logger.info("%s" % http)
            logger.info("Send http rsponse Success..\n")
        else:
            logger.error("Unvalid msg_type(%s)" % msg_type)

    def get_rsp_body(self, listener_id):
        listener = Listener.objects.get(listener_id=listener_id)

        root_obj = {}
        listener_obj = {}
        lb_obj_list = []
        root_obj['listener'] = listener_obj

        listener_obj['admin_state_up'] = listener.admin_state_up
        listener_obj['connection_limit'] = listener.connection_limit
        listener_obj['description'] = listener.description
        listener_obj['listener_id'] = listener.listener_id

        listener_obj['loadbalancers'] = lb_obj_list
        lbs = Loadbalancer.objects.filter(listener_id=listener.id)
        for lb in lbs:
            lb_obj = {}
            lb_obj['id'] = lb.loadbalancer_id
            lb_obj_list.append(lb_obj)

        listener_obj['name'] = listener.name
        listener_obj['protocol'] = listener.protocol
        listener_obj['protocol_port'] = listener.protocol_port
        listener_obj['stat_port'] = listener.stat_port

        return root_obj, listener_obj

    def update_listener_info(self, listener, request):
        required_flag = True
        if request.method == "POST":
            if not 'name' in request.data or request.data["name"]=="":
                required_flag = False
            if not 'protocol' in request.data or request.data["protocol"]=="":
                required_flag = False
            if not 'protocol_port' in request.data or request.data["protocol_port"]=="":
                required_flag = False
            if not 'stat_port' in request.data or request.data["stat_port"]=="":
                required_flag = False

        if required_flag == False:
            logger.error("Mandatory fields do not exist!")
            return None

        try:
            if 'name' in request.data and request.data["name"]:
                listener.name = request.data["name"]
            if 'protocol' in request.data and request.data["protocol"]:
                listener.protocol = request.data["protocol"]
            if 'protocol_port' in request.data and request.data["protocol_port"]:
                listener.protocol_port = request.data["protocol_port"]
            if 'stat_port' in request.data and request.data["stat_port"]:
                listener.stat_port = request.data["stat_port"]
            if 'description' in request.data and request.data["description"]:
                listener.description = request.data["description"]
            if 'admin_state_up' in request.data and request.data["admin_state_up"]:
                listener.admin_state_up = request.data["admin_state_up"]
            if 'connection_limit' in request.data and request.data["connection_limit"]:
                listener.connection_limit = request.data["connection_limit"]
        except KeyError as err:
            logger.error("JSON Key error: %s" % str(err))
            return None

        listener.save()
        return listener

    def check_listener_id(self, listener_id):
        try:
            listener = Listener.objects.get(listener_id=listener_id)
            return listener
        except Exception as err:
            logger.error("%s (listener_id=%s)" % ((str(err), listener_id)))
            return None

    # GET: /api/tenant/listeners
    def list(self, request):
        self.print_message_log("REQ", request)
        queryset = self.filter_queryset(self.get_queryset())

        root_obj = {}
        listener_obj_list = []
        root_obj['listeners'] = listener_obj_list

        for listener in queryset:
            temp_obj, listener_obj = self.get_rsp_body(listener.listener_id)
            listener_obj_list.append(listener_obj)

        self.print_message_log("RSP", root_obj)
        return Response(root_obj)

    # POST: /api/tenant/listeners
    def create(self, request):
        self.print_message_log("REQ", request)

        listener = Listener()
        listener.listener_id = str(uuid.uuid4())

        listener = self.update_listener_info(listener, request)
        if listener == None:
            return Response("Error: Mandatory fields not exist!", status=status.HTTP_400_BAD_REQUEST)

        rsp_data, listener_obj = self.get_rsp_body(listener.listener_id)

        lb_thr = threading.Thread(target=update_loadbalancer_model, args=(listener.listener_id,))
        lb_thr.start()

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_201_CREATED)

    # GET: /api/tenant/listeners/{listener_id}
    def retrieve(self, request, pk=None):
        self.print_message_log("REQ", request)

        if self.check_listener_id(pk) is None:
            return Response("Error: listener_id does not exist in Listener table", status=status.HTTP_404_NOT_FOUND)

        rsp_data, listener_obj = self.get_rsp_body(pk)

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data)

    # PUT: /api/tenant/listeners/{listener_id}
    def update(self, request, pk=None):
        self.print_message_log("REQ", request)

        listener = self.check_listener_id(pk)
        if listener is None:
            return Response("Error: listener_id does not exist in Listener table", status=status.HTTP_404_NOT_FOUND)

        listener = self.update_listener_info(listener, request)
        if listener == None:
            return Response("Error: Mandatory fields not exist!", status=status.HTTP_400_BAD_REQUEST)

        rsp_data, listener_obj = self.get_rsp_body(pk)

        lb_thr = threading.Thread(target=update_loadbalancer_model, args=(pk,))
        lb_thr.start()

        self.print_message_log("RSP", rsp_data)
        return Response(rsp_data, status=status.HTTP_202_ACCEPTED)

    # DELETE: /api/tenant/listeners/{listener_id}
    def destroy(self, request, pk=None):
        self.print_message_log("REQ", request)

        listener = self.check_listener_id(pk)
        if listener is None:
            return Response("Error: listener_id does not exist in Listener table", status=status.HTTP_404_NOT_FOUND)

        try:
            lb = Loadbalancer.objects.get(listener_id=listener.id)
            return Response("Error: There is a loadbalancer that uses listener_id", status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            logger.error("%s" % str(err))

        lb_thr = threading.Thread(target=update_loadbalancer_model, args=(pk,))
        lb_thr.start()

        Listener.objects.filter(listener_id=pk).delete()

        self.print_message_log("RSP", "")
        return Response(status=status.HTTP_204_NO_CONTENT)
