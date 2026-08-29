import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = os.path.dirname(__file__)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "recovery_training_data.csv",
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models",
)

os.makedirs(MODEL_DIR, exist_ok=True)


def load_data():

    df = pd.read_csv(DATA_PATH)

    # ID is useful for identification but not prediction.
    df = df.drop(
        columns=["transaction_id"],
        errors="ignore",
    )

    return df


def build_preprocessor(X):

    categorical_features = [
        "currency",
        "payment_method",
        "transaction_type",
        "failure_reason",
        "customer_segment",
        "preferred_payment_method",
    ]

    numerical_features = [
        "amount",
        "attempt_number",
        "successful_payments",
        "lifetime_value",
        "previous_recoveries",
    ]

    boolean_features = [
        "is_recoverable",
        "requires_review",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
            (
                "numerical",
                StandardScaler(),
                numerical_features,
            ),
            (
                "boolean",
                "passthrough",
                boolean_features,
            ),
        ]
    )

    return preprocessor


def evaluate_model(name, model, X_test, y_test):

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    metrics = {
        "model": name,
        "accuracy": accuracy_score(
            y_test,
            predictions,
        ),
        "precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "roc_auc": roc_auc_score(
            y_test,
            probabilities,
        ),
    }

    return metrics


def main():

    print()
    print("======================================")
    print("      RECOVEROS ML TRAINING")
    print("======================================")

    df = load_data()

    print(f"Training rows: {len(df)}")

    X = df.drop(
        columns=["recovered"]
    )

    y = df["recovered"]

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )
    )

    preprocessor = build_preprocessor(
        X_train
    )

    models = {

        "Logistic Regression":
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
            ),

        "Random Forest":
            RandomForestClassifier(
                n_estimators=300,
                max_depth=10,
                min_samples_leaf=3,
                class_weight="balanced",
                random_state=42,
            ),
    }

    results = []

    trained_models = {}

    for name, estimator in models.items():

        print()
        print(f"Training {name}...")

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor,
                ),
                (
                    "model",
                    estimator,
                ),
            ]
        )

        pipeline.fit(
            X_train,
            y_train,
        )

        metrics = evaluate_model(
            name,
            pipeline,
            X_test,
            y_test,
        )

        results.append(metrics)

        trained_models[name] = pipeline

        print(
            f"Accuracy : {metrics['accuracy']:.3f}"
        )

        print(
            f"Precision: {metrics['precision']:.3f}"
        )

        print(
            f"Recall   : {metrics['recall']:.3f}"
        )

        print(
            f"F1       : {metrics['f1']:.3f}"
        )

        print(
            f"ROC-AUC  : {metrics['roc_auc']:.3f}"
        )

    results_df = pd.DataFrame(results)

    print()
    print("======================================")
    print("           MODEL COMPARISON")
    print("======================================")

    print(
        results_df.to_string(
            index=False
        )
    )

    # Select based on ROC-AUC.
    best_name = (
        results_df
        .sort_values(
            "roc_auc",
            ascending=False,
        )
        .iloc[0]["model"]
    )

    best_model = trained_models[
        best_name
    ]

    model_path = os.path.join(
        MODEL_DIR,
        "recovery_model.joblib",
    )

    joblib.dump(
        best_model,
        model_path,
    )

    results_path = os.path.join(
        MODEL_DIR,
        "model_metrics.csv",
    )

    results_df.to_csv(
        results_path,
        index=False,
    )

    print()
    print(
        f"Best model: {best_name}"
    )

    print(
        f"Saved model to:\n{model_path}"
    )

    print(
        f"Saved metrics to:\n{results_path}"
    )

    print()
    print("======================================")
    print("       MODEL TRAINING COMPLETE")
    print("======================================")


if __name__ == "__main__":
    main()