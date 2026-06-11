from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from ml.features import extract_features


class ProficiencyClassifier:
    MODEL_PATH = str(Path(__file__).resolve().parent / "model.pkl")
    LABELS = ["beginner", "intermediate", "advanced"]

    def train(self, X, y):
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        joblib.dump(model, self.MODEL_PATH)
        return model

    def predict(self, features: np.ndarray) -> dict:
        model = joblib.load(self.MODEL_PATH)
        features = features.reshape(1, -1)
        predicted_level = model.predict(features)[0]
        proba = model.predict_proba(features)[0]
        probabilities = dict(zip(model.classes_, proba.tolist()))
        confidence = float(max(proba))
        return {
            "predicted_level": predicted_level,
            "confidence": confidence,
            "probabilities": probabilities,
        }

    def should_promote(self, user_id, db_session) -> dict:
        from models import User

        user = db_session.get(User, user_id)
        current_level = user.level if user else None

        features, session_count = extract_features(user_id, db_session)
        if features is None or session_count < 5:
            return {
                "should_promote": False,
                "reason": "insufficient_data",
                "current_level": current_level,
            }

        try:
            prediction = self.predict(features)
        except FileNotFoundError:
            return {
                "should_promote": False,
                "reason": "model_not_trained",
                "current_level": current_level,
            }

        score_trend = features[3]
        should_promote = (
            prediction["predicted_level"] != current_level
            and prediction["confidence"] > 0.75
            and score_trend > 0
        )
        return {
            "should_promote": should_promote,
            "predicted_level": prediction["predicted_level"],
            "confidence": prediction["confidence"],
            "current_level": current_level,
        }
