from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Node(models.Model):
    node_latitude = models.FloatField()
    node_longitude = models.FloatField()

    name = models.CharField(max_length=100)

    adjacent_nodes = models.ManyToManyField('self', blank=True, symmetrical=False)

    def __str__(self):
        return f"{self.name} --> ({self.node_latitude, self.node_longitude})"

    @property
    def coordinates(self):
        """to grab the lat/lng as a pair"""
        return (self.node_latitude,self.node_longitude)

class Edge(models.Model):
    # where the edge starts
    from_node = models.ForeignKey(Node, on_delete=models.CASCADE,related_name='outbound_roads')
    
    # where the edge ends
    to_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='inbound_roads')

    class Meta:
        # prevents duplicate roads
        unique_together = ('from_node', 'to_node')

    def clean(self):
        if self.from_node == self.to_node:
            raise ValidationError("A road cannot start and end at the exact same node!")
        
    def save(self, *args, **kwargs):
        
        self.full_clean() 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.from_node.name} -> {self.to_node.name}"