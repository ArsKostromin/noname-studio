from datetime import datetime, date
from typing import Dict, List, Any
from collections import defaultdict

from services.core_api import CoreAPIClient


# -------------------------------
# Расписание → фичи
# -------------------------------
def extract_schedule_features(schedule: List[Dict[str, Any]]) -> Dict[str, Dict]:
    """
    По каждой теме:
    - is_test
    - is_exam
    - days_until_event
    """
    today = date.today()
    features = {}

    for item in schedule:
        topic = item.get("topic")
        if not topic:
            continue

        due_date = item.get("due_date")
        days_until = None

        if due_date:
            due = datetime.fromisoformat(due_date).date()
            days_until = (due - today).days

        features[topic] = {
            "is_test": item.get("is_test", False),
            "is_exam": item.get("is_exam", False),
            "days_until_event": days_until,
        }

    return features


# -------------------------------
# Оценки → фичи
# -------------------------------
def extract_grade_features(grades_payload: List[Dict[str, Any]]) -> Dict[str, Dict]:
    """
    Агрегируем оценки по темам
    """
    topic_stats = defaultdict(lambda: {
        "scores": [],
        "weights": [],
        "fails": 0,
        "last_date": None,
    })

    for subject_block in grades_payload:
        for grade in subject_block["grades"]:
            topic = grade["topic"]
            value = grade["value"]
            weight = grade.get("weight", 1)
            work_date = grade.get("work_date")

            topic_stats[topic]["scores"].append(value)
            topic_stats[topic]["weights"].append(weight)

            if value < 4:
                topic_stats[topic]["fails"] += 1

            if work_date:
                dt = datetime.fromisoformat(work_date)
                last = topic_stats[topic]["last_date"]
                if last is None or dt > last:
                    topic_stats[topic]["last_date"] = dt

    result = {}
    today = datetime.utcnow()

    for topic, stats in topic_stats.items():
        avg = sum(s * w for s, w in zip(stats["scores"], stats["weights"])) / sum(stats["weights"])
        days_since = (today - stats["last_date"]).days if stats["last_date"] else None

        result[topic] = {
            "avg_score": round(avg, 2),
            "fails": stats["fails"],
            "days_since_last_grade": days_since,
        }

    return result


# -------------------------------
# 🔥 ГЛАВНАЯ ФУНКЦИЯ
# -------------------------------
async def collect_student_features(access_token: str) -> Dict[str, Dict]:
    """
    Собирает ВСЕ фичи студента:
    - оценки
    - расписание
    - объединяет по темам
    """

    client = CoreAPIClient(access_token)

    # 1️⃣ Получаем данные
    schedule = await client.get_my_schedule()
    grades = await client.get_my_grades()

    # 2️⃣ Извлекаем фичи
    schedule_features = extract_schedule_features(schedule)
    grade_features = extract_grade_features(grades)

    # 3️⃣ Склеиваем по темам
    all_topics = set(schedule_features) | set(grade_features)
    result = {}

    for topic in all_topics:
        result[topic] = {
            **grade_features.get(topic, {}),
            **schedule_features.get(topic, {}),
        }

    return result
