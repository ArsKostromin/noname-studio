"""
Presenter'ы для приложения grades - вынесение бизнес-логики из views
"""
from collections import defaultdict
from .models import Grade
from .serializers import GradeSerializer
from core.serializers import SubjectSerializer


class GradesPresenter:
    """Presenter для работы с оценками студента"""
    
    @staticmethod
    def get_student_grades_by_subject(student):
        """
        Получить оценки студента, сгруппированные по предметам с расчетом среднего балла.
        
        Args:
            student: Объект Student
            
        Returns:
            list: Список словарей с информацией о предметах и оценках
        """
        # Получаем все оценки студента
        grades = Grade.objects.filter(student=student).select_related("subject", "teacher")
        
        # Группируем по предметам
        grades_by_subject = defaultdict(list)
        for grade in grades:
            grades_by_subject[grade.subject].append(grade.value)
        
        # Формируем результат
        result = []
        for subject, values in grades_by_subject.items():
            avg_score = sum(values) / len(values)
            subject_data = SubjectSerializer(subject).data
            
            # Получаем все оценки по этому предмету
            subject_grades = grades.filter(subject=subject)
            grades_data = [GradeSerializer(grade).data for grade in subject_grades]
            
            result.append({
                'subject': subject_data,
                'grades': grades_data,
                'average_score': round(avg_score, 2),
                'total_grades': len(values)
            })
        
        return result

