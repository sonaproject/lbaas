
from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy
from synchronizers.new_base.exceptions import *

class Scheduler(object):
    # XOS Scheduler Abstract Base Class
    # Used to implement schedulers that pick which node to put instances on

    def __init__(self, slice):
        self.slice = slice

    def pick(self):
        # this method should return a tuple (node, parent)
        #    node is the node to instantiate on
        #    parent is for container_vm instances only, and is the VM that will
        #      hold the container

        raise Exception("Abstract Base")


class LeastLoadedNodeScheduler(Scheduler):
    # This scheduler always return the node with the fewest number of
    # instances.

    def __init__(self, slice, label=None):
        super(LeastLoadedNodeScheduler, self).__init__(slice)
        self.label = label

    def pick(self):
        # start with all nodes
        nodes = Node.objects.all()

        # if a label is set, then filter by label
        if self.label:
            nodes = nodes.filter(nodelabels__name=self.label)

        # if slice.default_node is set, then filter by default_node
        if self.slice.default_node:
            nodes = nodes.filter(name = self.slice.default_node)

        # convert to list
        nodes = list(nodes)

        # sort so that we pick the least-loaded node
        nodes = sorted(nodes, key=lambda node: node.instances.count())

        if not nodes:
            raise Exception(
                "LeastLoadedNodeScheduler: No suitable nodes to pick from")

        # TODO: logic to filter nodes by which nodes are up, and which
        #   nodes the slice can instantiate on.
        return [nodes[0], None]


class LoadbalancerPolicy(Policy):
    model_name = "Loadbalancer"

    def handle_create(self, tenant):
        return self.handle_update(tenant)

    def handle_update(self, tenant):
        self.manage_container(tenant)

    def save_instance(self, instance):
        # Override this function to do custom pre-save or post-save processing,
        # such as creating ports for containers.
        instance.save()

    def manage_container(self, tenant):
        if tenant.deleted:
            return

        if tenant.instance is None:
            if not tenant.owner.slices.count():
                raise SynchronizerConfigurationError("The service has no slices")

            new_instance_created = False
            slice = [s for s in tenant.owner.slices.all() if tenant.slice_name in s.name]
            slice = slice[0]

            desired_image = slice.default_image

            flavor = slice.default_flavor
            if not flavor:
                flavors = Flavor.objects.filter(name="m1.small")
                if not flavors:
                    raise SynchronizerConfigurationError("No m1.small flavor")
                flavor = flavors[0]

            if slice.default_isolation == "container_vm":
                raise Exception("Not implemented")
            else:
                (node, parent) = LeastLoadedNodeScheduler(slice).pick()

            assert(slice is not None)
            assert(node is not None)
            assert(desired_image is not None)
            assert(tenant.creator is not None)
            assert(node.site_deployment.deployment is not None)
            assert(flavor is not None)

            try:
                instance = Instance(slice=slice,
                                    node=node,
                                    image=desired_image,
                                    creator=tenant.creator,
                                    deployment=node.site_deployment.deployment,
                                    flavor=flavor,
                                    isolation=slice.default_isolation,
                                    parent=parent)
                self.save_instance(instance)
                new_instance_created = True

                tenant.instance = instance
                tenant.save()
            except:
                # NOTE: We don't have transactional support, so if the synchronizer crashes and exits after
                #       creating the instance, but before adding it to the tenant, then we will leave an
                #       orphaned instance.
                if new_instance_created:
                    instance.delete()
