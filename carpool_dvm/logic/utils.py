from collections import deque
from roadmap.models import Edge, Node
from .models import Trip, Carpool_request
from django.shortcuts import render

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


# def find_requested_trips(Carpool_request):

#     start_id = Carpool_request.start_node.id
#     end_id = Carpool_request.end_node.id
    
#     active_trips = Trip.objects.filter(is_active = True, available_seats__gt = 0 )
#     matching_trips = []

#     for trip in active_trips:
#         remaining_route_dicts = trip.route[trip.current_node_index:]
#         remaining_ids = [node['id'] for node in remaining_route_dicts]

#         if start_id in remaining_ids and end_id in remaining_ids:

#             if remaining_ids.index(start_id) < remaining_ids.index(end_id):
#                 matching_trips.append(trip)
                
#     return matching_trips


def meeting_point(RideRequest, trip):
    """
    Finds the intersection points for Start and End nodes.
    Returns: Dict containing the meeting node ID and the 'cost' (hops).
    """

    route_ids = {node['id'] for node in trip.route}

    def find_best_connection(target_node):
        """
        Inner helper checks proximity layers 0, 1, and 2.
        Returns: (meeting_node_id, hops) or None
        """
        # --- LAYER 0: Direct Match (0 Hops) ---
        if target_node.id in route_ids:
            return {'id': target_node.id, 'hops': 0}

        # --- LAYER 1: Immediate Neighbors (1 Hop) ---
        first_layer_neighbors = target_node.adjacent_nodes.all()
        
        for neighbor in first_layer_neighbors:
            if neighbor.id in route_ids:
                return {'id': neighbor.id, 'hops': 1}

        # --- LAYER 2: Neighbors of Neighbors (2 Hops) ---
        for neighbor in first_layer_neighbors:
            # FIX: Use 'neighbor' loop correctly here
            for second_neighbor in neighbor.adjacent_nodes.all():
                if second_neighbor.id in route_ids:
                    return {'id': second_neighbor.id, 'hops': 2}
        
        return None

    # 2. Run the check for both Start and End
    start_match = find_best_connection(RideRequest.start_node)
    end_match = find_best_connection(RideRequest.end_node)
    
    # 3. Only return if BOTH match
    if start_match and end_match:
        return {
            "pickup": start_match,  # e.g., {'id': 55, 'hops': 1}
            "dropoff": end_match    # e.g., {'id': 92, 'hops': 0}
        }
    
    return None


def potential_ride_requests(active_trip):
    pending_requests = Carpool_request.objects.filter(status = "Pending")
    recommendations = []

    route_map = {node['id'] : index for index, node in enumerate(active_trip.route)}

    for req in pending_requests:
        match_data = meeting_point(req, active_trip)

        if match_data:
            pickup_node_id = match_data["pickup"]["id"]
            dropoff_node_id = match_data["dropoff"]["id"]

            pickup_index = route_map[pickup_node_id]
            dropoff_index = route_map[dropoff_node_id]

            if (pickup_index < dropoff_index) and (pickup_index >= active_trip.current_node_index):

                req.pickup_info = match_data["pickup"]
                req.dropoff_info = match_data["dropoff"]

                req.detour_hops = (match_data['pickup']['hops'] + match_data['dropoff']['hops']) * 2

                recommendations.append(req)

    return recommendations






    