from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy
from synchronizers.new_base.exceptions import *

from synchronizers.new_base.model_policies.model_policy_tenantwithcontainer import Scheduler
from synchronizers.new_base.model_policies.model_policy_tenantwithcontainer import LeastLoadedNodeScheduler


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
