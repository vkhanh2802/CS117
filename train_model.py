from pathlib import Path
import json
import platform

import joblib
import lightgbm
import numpy as np
import pandas as pd
import sklearn
import xgboost
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier


DATA_PATH = Path("train.csv")
OUTPUT_DIR = Path("outputs")
TARGET_COL = "procrastination_level"

LABEL_MAP = {"Low": 0, "Medium": 1, "High": 2}


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce")
    result["hour"] = result["timestamp"].dt.hour
    result["day_of_week"] = result["timestamp"].dt.dayofweek
    result["is_weekend"] = result["day_of_week"].isin([5, 6]).astype(int)
    return result


def build_training_data(df: pd.DataFrame):
    df = add_time_features(df).dropna(subset=[TARGET_COL]).copy()
    df[TARGET_COL] = df[TARGET_COL].map(LABEL_MAP)

    if df[TARGET_COL].isnull().any():
        raise ValueError("Có nhãn procrastination_level không hợp lệ.")

    y = df[TARGET_COL].astype(int)
    X = df.drop(columns=[TARGET_COL, "student_id", "timestamp"], errors="ignore")

    categorical_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numerical_cols = X.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()
    return X, y, categorical_cols, numerical_cols


def build_preprocessor(categorical_cols, numerical_cols):
    try:
        onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        onehot = OneHotEncoder(handle_unknown="ignore", sparse=False)

    return ColumnTransformer(
        transformers=[
            ("cat", onehot, categorical_cols),
            ("num", StandardScaler(), numerical_cols),
        ],
        remainder="drop",
    )


def build_models():
    return {
        "Decision Tree": DecisionTreeClassifier(max_depth=None, random_state=42, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=None, random_state=42, class_weight="balanced", n_jobs=-1),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "XGBoost": XGBClassifier(n_estimators=400, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, objective="multi:softprob", num_class=3, eval_metric="mlogloss", random_state=42, n_jobs=-1),
        "LightGBM": LGBMClassifier(n_estimators=400, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, objective="multiclass", random_state=42, n_jobs=-1, verbose=-1),
    }


def collect_environment_metadata(best_model_name: str) -> dict:
    return {
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scikit_learn": sklearn.__version__,
        "joblib": joblib.__version__,
        "xgboost": xgboost.__version__,
        "lightgbm": lightgbm.__version__,
        "best_model": best_model_name,
    }


def train_and_save():
    OUTPUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    X, y, categorical_cols, numerical_cols = build_training_data(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    results = []
    trained_pipelines = {}

    for model_name, model in build_models().items():
        pipeline = Pipeline(steps=[("preprocessor", build_preprocessor(categorical_cols, numerical_cols)), ("model", model)])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        results.append({
            "model": model_name,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision_weighted": precision_score(y_test, y_pred, average="weighted", zero_division=0),
            "recall_weighted": recall_score(y_test, y_pred, average="weighted", zero_division=0),
            "f1_weighted": f1_score(y_test, y_pred, average="weighted", zero_division=0),
        })
        trained_pipelines[model_name] = pipeline

    results_df = pd.DataFrame(results).sort_values("f1_weighted", ascending=False)
    results_df.to_csv(OUTPUT_DIR / "model_results.csv", index=False)

    best_model_name = results_df.iloc[0]["model"]
    best_pipeline = trained_pipelines[best_model_name]
    joblib.dump(best_pipeline, OUTPUT_DIR / "best_model.joblib")

    metadata = collect_environment_metadata(best_model_name)
    (OUTPUT_DIR / "model_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    with open(OUTPUT_DIR / "best_model_info.txt", "w", encoding="utf-8") as f:
        f.write(f"Best model: {best_model_name}\n")
        f.write("Label mapping:\nLow -> 0\nMedium -> 1\nHigh -> 2\n")
        f.write(f"scikit-learn: {sklearn.__version__}\n")

    print(results_df.to_string(index=False))
    print(f"\nĐã lưu mô hình tốt nhất: {best_model_name}")
    print(f"Đã lưu metadata môi trường: {OUTPUT_DIR / 'model_metadata.json'}")


if __name__ == "__main__":
    train_and_save()
