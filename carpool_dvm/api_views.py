from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from logic.models import Trip

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_driver_location_api(request):
    arrived_node_index = request.data.get('current_node_index')

    if not arrived_node_index:
        return Response({"error" : "Missing current_node_index" }, status=400)

    try:
        trip = Trip.objects.get(driver = request.user, is_available =True)
    except Trip.DoesNotExist : 
        return Response({"error": "No active trip found."}, status=404)

    route_list = trip.route

    if arrived_node_index in route_list: 
        new_index = route_list.index(arrived_node_index)

        if new_index >= trip.current_node_index:
            trip.current_node_index = new_index
            trip.save()

            return Response({"messages": f"pointer moved to {new_index}"}, status=200)
        else:
            return Response({"error": "Cannot move backwards on the route."}, status=400)
        
    else:
        return Response({"error": "Node not found in route."}, status=400)