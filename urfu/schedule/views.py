from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Schedule
from .serializers import ScheduleSerializer


class ScheduleViewSet(ReadOnlyModelViewSet):
    queryset = Schedule.objects.select_related("subject", "group", "teacher")
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        group_id = self.request.query_params.get("group")
        weekday = self.request.query_params.get("weekday")

        if group_id:
            qs = qs.filter(group_id=group_id)

        if weekday:
            qs = qs.filter(weekday=weekday)

        return qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_schedule(request):
    """
    Эндпоинт для получения расписания текущего пользователя.
    Возвращает расписание студента с темами, контрольными, тестами и т.д.
    """
    student = request.user
    schedule_items = Schedule.objects.filter(
        group=student.group
    ).select_related("subject", "group", "teacher").order_by('weekday', 'starts_at')
    
    serializer = ScheduleSerializer(schedule_items, many=True)
    return Response(serializer.data)
