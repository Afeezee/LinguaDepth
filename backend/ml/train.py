"""Train the proficiency classifier from collected session data.

Run manually from the backend/ directory:
    python ml/train.py

Uses each user's placement-assigned level as the ground truth label and
requires at least 5 completed sessions per user.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from app import create_app
from ml.classifier import ProficiencyClassifier
from ml.features import extract_features
from models import Session, User, db


def build_dataset():
    X, y = [], []
    for user in User.query.all():
        completed = Session.query.filter_by(user_id=user.id, completed=True).count()
        if completed < 5:
            continue
        features, _ = extract_features(user.id, db.session)
        if features is None:
            continue
        X.append(features)
        y.append(user.level)
    return np.array(X), np.array(y)


def main():
    app = create_app()
    with app.app_context():
        X, y = build_dataset()

    if len(X) < 10:
        print(f"Not enough training data: {len(X)} users with 5+ sessions (need 10+).")
        sys.exit(1)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if len(set(y)) > 1 else None
    )

    classifier = ProficiencyClassifier()
    model = classifier.train(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print(classification_report(y_test, y_pred))
    print(f"Model saved to {classifier.MODEL_PATH}")


if __name__ == "__main__":
    main()
