# -*- coding: utf-8 -*-
#
from perms.models import UserGrantedMappingNode
from rest_framework.exceptions import PermissionDenied
from common.exceptions import JMSObjectDoesNotExist
from perms.async_tasks.mapping_node_task import submit_update_mapping_node_task_for_user
from ...hands import Node, Asset


class UserGrantedNodeAssetMixin:

    def list(self, request, *args, **kwargs):
        self.submit_update_mapping_node_task(user=self.request.user)
        return super().list(request, *args, **kwargs)

    def submit_update_mapping_node_task(self, user):
        submit_update_mapping_node_task_for_user(user)

    def dispatch_node_process(self, key, mapping_node: UserGrantedMappingNode, node: Node = None):
        if mapping_node is None:
            ancestor_keys = Node.get_node_ancestor_keys(key)
            granted = UserGrantedMappingNode.objects.filter(key__in=ancestor_keys, granted=True).exists()
            if not granted:
                raise JMSObjectDoesNotExist(object_name=Node._meta.object_name)
            queryset = self.on_granted_node(key, mapping_node, node)
        else:
            if mapping_node.granted:
                # granted_node
                queryset = self.on_granted_node(key, mapping_node, node)
            else:
                queryset = self.on_ungranted_node(key, mapping_node, node)
        return queryset

    def on_granted_node(self, key, mapping_node: UserGrantedMappingNode, node: Node = None):
        raise NotImplementedError

    def on_ungranted_node(self, key, mapping_node: UserGrantedMappingNode, node: Node = None):
        raise NotImplementedError
