from collections import deque
from roadmap.models import Edge, Node
from .models import Trip

def get_graph():
    edges = Edge.objects.all()
    graph = {}

    for edge in edges:
        u = edge.from_node_id
        v = edge.to_node_id

        if u not in graph:
            graph[u] = []

        graph[u].append(v)    

    return graph

def shortest_path(start_node_id, end_node_id):
    if start_node_id == end_node_id:
        return [start_node_id]

    graph = get_graph() 

    if start_node_id not in graph:
        return []

    queue = deque([(start_node_id, [start_node_id])])
    visited = {start_node_id}

    while queue:
        current_node, current_path  = queue.popleft()

        for neighbor in graph.get(current_node, []):
            if neighbor == end_node_id:
                return current_path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, current_path + [neighbor]))

    return []


def find_requested_trip(Carpool_request):

    active_trips = Trip.objects.filter(is_available = True, available_seats__gt = 0 )

    start_id = Carpool_request.start_node.id
    end_id = Carpool_request.end_node.id

    for trip in active_trips:
        remaining_route_dicts = trip.route[trip.current_node_index:]
        remaining_ids = [node['id'] for node in remaining_route_dicts]

        if start_id in remaining_ids and end_id in remaining_ids:

            if remaining_ids.index(start_id) < remaining_ids.index(end_id):

                return trip

    return None