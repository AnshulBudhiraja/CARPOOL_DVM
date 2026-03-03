from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Node, Edge

@receiver(m2m_changed, sender=Node.adjacent_nodes.through)
def create_edge(sender, instance, action, pk_set, **kwargs):
    
    if action == "post_add":
        for neighbor_id in pk_set:
            neighbor = Node.objects.get(pk=neighbor_id)
            edge, created = Edge.objects.get_or_create(from_node= instance, to_node= neighbor)

    elif action == "post_remove":
        for neighbor_id in pk_set:
            Edge.objects.filter(from_node=instance, to_node= neighbor_id).delete()

