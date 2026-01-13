from datetime import datetime, date, time
from typing import Dict, List, Any, Tuple
from collections import defaultdict

from services.core_api import CoreAPIClient


# -------------------------------
# utils
# -------------------------------

def time_to_minutes(t: str | None) -> int | None:
    if not t:
        return None
    hh, mm, *_ = t.split(":")
    return int(hh) * 60 + int(mm)


def topic_key(subject_title: str, topic: str) -> Tuple[str, str]:
    return subject_title.strip(), topic.strip()


# -------------------------------
# Расписание → фичи
# -------------------------------

def extract_schedule_features(schedule: List[Dict[str, Any]]) -> Dict[Tuple[str, str], Dict]:
    today = date.today()
    features = {}

    for item in schedule:
        topic = item.get("topic")
        subject = item.get("subject", {}).get("title")

        if not topic or not subject:
            continue

        due_date = item.get("due_date")
        days_until = None

        if due_date:
            try:
                due = datetime.fromisoformat(due_date).date()
                days_until = (due - today).days
            except Exception:
                days_until = None

        key = topic_key(subject, topic)

        features[key] = {
            "subject": subject,
            "topic": topic,

            "weekday": item.get("weekday"),

            "starts_at_min": time_to_minutes(item.get("starts_at")),
            "ends_at_min": time_to_minutes(item.get("ends_at")),

            "teacher_department": item.get("teacher", {}).get("department"),

            "is_test": item.get("is_test", False),
            "is_exam": item.get("is_exam", False),
            "is_lab": item.get("is_lab_work", False),
            "is_control": item.get("is_control_work", False),
            "is_final": item.get("is_final", False),

            "max_score": item.get("max_score"),
            "days_until_event": days_until,
        }

    return features


# -------------------------------
# Оценки → фичи
# -------------------------------

def extract_grade_features(grades_payload: List[Dict[str, Any]]) -> Dict[Tuple[str, str], Dict]:
    topic_stats = defaultdict(lambda: {
        "scores": [],
        "weights": [],
        "fails": 0,
        "last_date": None,
    })

    for subject_block in grades_payload:
        subject = subject_block.get("subject", {}).get("title")
        if not subject:
            continue

        for grade in subject_block.get("grades", []):
            topic = grade.get("topic")
            if not topic:
                continue

            value = grade.get("value")
            weight = grade.get("weight", 1)
            work_date = grade.get("work_date")

            key = topic_key(subject, topic)

            if value is not None:
                topic_stats[key]["scores"].append(value)
                topic_stats[key]["weights"].append(weight)

                if value < 4:
                    topic_stats[key]["fails"] += 1

            if work_date:
                try:
                    dt = datetime.fromisoformat(work_date)
                    last = topic_stats[key]["last_date"]
                    if last is None or dt > last:
                        topic_stats[key]["last_date"] = dt
                except Exception:
                    pass

    result = {}
    today = datetime.utcnow()

    for key, stats in topic_stats.items():
        if stats["weights"]:
            avg = sum(s * w for s, w in zip(stats["scores"], stats["weights"])) / sum(stats["weights"])
            min_score = min(stats["scores"])
            max_score = max(stats["scores"])
            total = len(stats["scores"])
        else:
            avg = None
            min_score = None
            max_score = None
            total = 0

        days_since = (today - stats["last_date"]).days if stats["last_date"] else None

        subject, topic = key

        result[key] = {
            "subject": subject,
            "topic": topic,

            "avg_score": round(avg, 3) if avg is not None else None,
            "min_score": min_score,
            "max_score": max_score,
            "total_works": total,
            "fails": stats["fails"],
            "days_since_last_grade": days_since,
        }

    return result


# -------------------------------
# 🔥 ГЛАВНАЯ ФУНКЦИЯ
# -------------------------------

async def collect_student_features(access_token: str) -> Dict[str, Dict]:
    """
    Собирает расширенные фичи студента для ML:
    - оценки
    - расписание
    - объединение по (subject, topic)
    """

    client = CoreAPIClient(access_token)

    # 1️⃣ Получаем данные
    schedule = await client.get_my_schedule()
    grades = await client.get_my_grades()

    # 2️⃣ Извлекаем фичи
    schedule_features = extract_schedule_features(schedule)
    grade_features = extract_grade_features(grades)

    # 3️⃣ Склеиваем
    all_keys = set(schedule_features) | set(grade_features)
    result = {}

    for key in all_keys:
        subject, topic = key

        merged = {
            "subject": subject,
            "topic": topic,
        }

        merged.update(grade_features.get(key, {}))
        merged.update(schedule_features.get(key, {}))

        result[f"{subject} :: {topic}"] = merged

    return result
