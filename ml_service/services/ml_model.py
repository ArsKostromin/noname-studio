from typing import Dict, Any
import random


def predict_topic_needs(features: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Принимает фичи по темам и возвращает:
    - need_review: нужно ли повторить
    - score: условная уверенность (0–1)
    - cluster: псевдо-кластер (потом будет KMeans)
    """

    result = {}

    for topic, data in features.items():
        avg_score = data.get("avg_score")
        fails = data.get("fails", 0)
        days_until = data.get("days_until_event")

        # простая эвристика, без магии
        need_review = False

        if avg_score is not None and avg_score < 4:
            need_review = True

        if fails >= 1:
            need_review = True

        if days_until is not None and days_until <= 3:
            need_review = True

        result[topic] = {
            "need_review": need_review,
            "score": round(random.uniform(0.3, 0.9), 2),
            "cluster": random.randint(0, 2),
        }

    return result
