"""
Presenter'ы для приложения schedule - вынесение бизнес-логики из views
"""
from .models import Schedule
from .serializers import ScheduleSerializer


class SchedulePresenter:
    """Presenter для работы с расписанием студента"""
    
    @staticmethod
    def get_student_schedule(student):
        """
        Получить расписание студента по всем его группам.
        
        Args:
            student: Объект Student
            
        Returns:
            QuerySet: QuerySet с расписанием студента
        """
        # Получаем все группы студента
        student_groups = student.groups.all()
        
        # Фильтруем расписание по всем группам студента
        schedule_items = Schedule.objects.filter(
            group__in=student_groups
        ).select_related("subject", "group", "teacher").order_by('weekday', 'starts_at')
        
        return schedule_items
    
    @staticmethod
    def serialize_schedule(schedule_queryset):
        """
        Сериализовать расписание.
        
        Args:
            schedule_queryset: QuerySet с расписанием
            
        Returns:
            list: Список сериализованных данных
        """
        serializer = ScheduleSerializer(schedule_queryset, many=True)
        return serializer.data

