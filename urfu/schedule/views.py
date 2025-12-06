from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Schedule
from .serializers import ScheduleSerializer
from .presenters import SchedulePresenter
from .schemas import my_schedule_schema, schedule_list_schema


class ScheduleViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с расписанием.
    Предоставляет только чтение (ReadOnly) с возможностью фильтрации.
    """
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
    
    @schedule_list_schema
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@my_schedule_schema
def my_schedule(request):
    """
    Эндпоинт для получения расписания текущего пользователя.
    Возвращает расписание студента с темами, контрольными, тестами и т.д.
    Студент может быть в нескольких группах (одна группа = один предмет).
    """
    student = request.user
    schedule_items = SchedulePresenter.get_student_schedule(student)
    serialized_data = SchedulePresenter.serialize_schedule(schedule_items)
    return Response(serialized_data)
