from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from logic.models import Trip

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_driver_location_api(request):
    arrived_node_index = request.data.get('current_node_index')

    if arrived_node_index is None:
        return Response({"error": "Missing current_node_index"}, status=400)

    try:
        arrived_node_index = int(arrived_node_index)
    except (TypeError, ValueError):
        return Response({"error": "current_node_index must be an integer"}, status=400)

    try:
        trip = Trip.objects.get(driver=request.user, is_active=True, status = 'Active')
    except Trip.DoesNotExist:
        return Response({"error": "No active trip found."}, status=404)

    route_list = trip.route  # list of dicts: [{"id": .., "name": ..}, ...]

    if not route_list or arrived_node_index >= len(route_list):
        return Response({"error": "Node index out of route range."}, status=400)

    if arrived_node_index > trip.current_node_index:
        trip.current_node_index = arrived_node_index
        trip.save()
        return Response({"message": f"Location updated to stop {arrived_node_index + 1} — {route_list[arrived_node_index].get('name', '')}"}, status=200)
    elif arrived_node_index == trip.current_node_index:
        return Response({"error": "Already at this stop."}, status=400)
    else:
        return Response({"error": "Cannot move backwards on the route."}, status=400)
