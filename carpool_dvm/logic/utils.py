from collections import deque
from roadmap.models import Edge, Node
from .models import Trip, Carpool_request
from django.shortcuts import render, get_object_or_404

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
    # Include the current node so passengers at the driver's current stop are found
    remaining_route = active_trip.route[active_trip.current_node_index:]
    remaining_route_ids = set(node['id'] for node in remaining_route)

    # Fetch ALL pending requests — the old start_node__id__in filter was too strict:
    # it excluded passengers whose start_node is 1-2 hops off-route (off the exact
    # route nodes), which meeting_point is specifically designed to handle.
    pending_requests = Carpool_request.objects.filter(status="Pending").select_related(
        'passenger', 'start_node', 'end_node'
    )
    recommendations = []

    route_map = {node['id']: index for index, node in enumerate(active_trip.route)}

    for req in pending_requests:
        match_data = meeting_point(req, active_trip)

        if not match_data:
            continue

        pickup_node_id = match_data["pickup"]["id"]
        dropoff_node_id = match_data["dropoff"]["id"]

        # Guard against nodes not in route_map
        pickup_index = route_map.get(pickup_node_id)
        dropoff_index = route_map.get(dropoff_node_id)

        if pickup_index is None or dropoff_index is None:
            continue

        # Pickup must be at/ahead of current stop, before dropoff, and still on remaining route
        if (pickup_index < dropoff_index) and (pickup_index >= active_trip.current_node_index) and (pickup_node_id in remaining_route_ids):
            req.pickup_info = match_data["pickup"]
            req.dropoff_info = match_data["dropoff"]
            req.detour_hops = (match_data['pickup']['hops'] + match_data['dropoff']['hops']) * 2
            recommendations.append(req)

    return recommendations



def passenger_route(carpool_request, trip):
    
    start_node_id = carpool_request.start_node.id
    end_node_id = carpool_request.end_node.id

    if not carpool_request or not trip:
        return []
    
    matched_route = trip.route

    matched_route_ids = [node['id'] for node in matched_route]
    nearest_nodes_in_matched_route = meeting_point(carpool_request, trip)

    extra_route_ids_from_start = shortest_path(start_node_id, nearest_nodes_in_matched_route["pickup"]["id"])
    extra_route_ids_from_end = shortest_path(nearest_nodes_in_matched_route["dropoff"]["id"], end_node_id)

    start_idx = matched_route_ids.index(nearest_nodes_in_matched_route["pickup"]["id"])
    end_idx = matched_route_ids.index(nearest_nodes_in_matched_route["dropoff"]["id"])
    ride_segment_ids = matched_route_ids[start_idx : end_idx + 1]

    passenger_route_ids = []
    for id in extra_route_ids_from_start:
        passenger_route_ids.append(id)

    for id in ride_segment_ids[1:]:
        passenger_route_ids.append(id)

    for id in extra_route_ids_from_end[1:]:
        passenger_route_ids.append(id)

    passenger_route = []
    passenger_route_nodes = Node.objects.filter(id__in = passenger_route_ids)
    passenger_node_dict = {n.id : n.name for n in passenger_route_nodes}

    for node_id in passenger_route_ids:
        passenger_route.append({
            "id" : node_id,
            "name": passenger_node_dict.get(node_id, "Unknown Node")
        })

    return passenger_route
        

def passenger_fare(carpool_request, trip, base_fee, price_per_hop):
    other_passengers_in_trip = trip.passengers.all()
    passenger_route_nodes = passenger_route(carpool_request,trip)
    passenger_route_nodes_ids = [node["id"] for node in passenger_route_nodes]

    paying_passengers_per_node = [0] * len(passenger_route_nodes)

    for passenger in other_passengers_in_trip:
        other_passenger_request = Carpool_request.objects.filter(
            passenger = passenger,
            status__in = ['Confirmed','In Progress']
        ).first()
        other_passenger_route_nodes = passenger_route(other_passenger_request, trip)
        other_passenger_route_nodes_ids = [node["id"] for node in other_passenger_route_nodes]
        other_passenger_route_set = set(other_passenger_route_nodes_ids)

        common_route = [node for node in passenger_route_nodes_ids if node in other_passenger_route_set]
        
        common_start_index = passenger_route_nodes_ids.index(common_route[0])
        common_end_index = passenger_route_nodes_ids.index(common_route[-1])

        if other_passenger_route_nodes_ids[-1] in common_route:
            for i in range(common_start_index,common_end_index):
                paying_passengers_per_node[i] += 1

        elif other_passenger_route_nodes_ids[-1] not in common_route:
            for i in range(common_start_index,common_end_index+1):
                paying_passengers_per_node[i] += 1

    for i in range(0,len(passenger_route_nodes)):
        paying_passengers_per_node[i] += 1 

    fare = price_per_hop * (sum(1.0/ni for ni in paying_passengers_per_node[:-1])) + base_fee

    for i in range(0,meeting_point(carpool_request, trip)["pickup"]["hops"]):
        if paying_passengers_per_node[i] == 1:
            fare += price_per_hop

    return fare



        


       

        
        




        