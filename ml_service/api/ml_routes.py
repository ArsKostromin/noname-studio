"""
Роуты для ML функционала
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
from loguru import logger

router = APIRouter()


class PredictionRequest(BaseModel):
    """Запрос для предсказания"""
    features: List[float]
    model_type: str = "logistic_regression"  # или "kmeans"


class PredictionResponse(BaseModel):
    """Ответ с предсказанием"""
    prediction: float
    probability: Optional[float] = None
    model_type: str


class ClusterRequest(BaseModel):
    """Запрос для кластеризации"""
    data: List[List[float]]
    n_clusters: int = 3


class ClusterResponse(BaseModel):
    """Ответ с кластерами"""
    labels: List[int]
    n_clusters: int


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Предсказание с помощью Logistic Regression
    
    Принимает признаки и возвращает предсказание с вероятностью.
    """
    try:
        features = np.array(request.features).reshape(1, -1)
        
        if request.model_type == "logistic_regression":
            # Здесь можно загрузить сохранённую модель или обучить новую
            # Для примера создаём простую модель
            model = LogisticRegression()
            # В реальности здесь должна быть загрузка обученной модели
            # model = joblib.load("models/logistic_regression.pkl")
            
            # Для демо создаём фиктивные данные для обучения
            X_demo = np.random.rand(100, len(request.features))
            y_demo = np.random.randint(0, 2, 100)
            model.fit(X_demo, y_demo)
            
            prediction = model.predict(features)[0]
            probability = model.predict_proba(features)[0].max()
            
            return PredictionResponse(
                prediction=float(prediction),
                probability=float(probability),
                model_type="logistic_regression"
            )
        else:
            raise HTTPException(status_code=400, detail="Unknown model type")
            
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cluster", response_model=ClusterResponse)
async def cluster(request: ClusterRequest):
    """
    Кластеризация данных с помощью K-Means
    
    Принимает массив данных и количество кластеров.
    """
    try:
        data = np.array(request.data)
        
        if len(data) < request.n_clusters:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough data points. Need at least {request.n_clusters}, got {len(data)}"
            )
        
        # Нормализация данных
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        
        # Кластеризация
        kmeans = KMeans(n_clusters=request.n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data_scaled)
        
        return ClusterResponse(
            labels=labels.tolist(),
            n_clusters=request.n_clusters
        )
        
    except Exception as e:
        logger.error(f"Clustering error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """
    Список доступных моделей
    """
    models_dir = "models/"
    models = []
    
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith((".pkl", ".joblib")):
                models.append(file)
    
    return {
        "available_models": models,
        "supported_types": ["logistic_regression", "kmeans"]
    }



