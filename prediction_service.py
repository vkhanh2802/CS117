from pathlib import Path
from datetime import datetime

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "outputs" / "best_model.joblib"
INV_LABEL_MAP = {0: "Low", 1: "Medium", 2: "High"}

APP_CATEGORIES = ["Social", "Gaming", "Productivity", "Entertainment", "System"]
TIME_OF_DAY = ["Morning", "Afternoon", "Evening", "Night"]
TASK_PRIORITIES = ["Low", "Medium", "High"]
TIME_TO_HOUR = {
    "Morning": 9,
    "Afternoon": 14,
    "Evening": 19,
    "Night": 23,
}
DISTRACTING_APPS = {"Social", "Gaming", "Entertainment"}


def _first(payload: dict, field_name: str):
    value = payload.get(field_name)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce")
    result["hour"] = result["timestamp"].dt.hour
    result["day_of_week"] = result["timestamp"].dt.dayofweek
    result["is_weekend"] = result["day_of_week"].isin([5, 6]).astype(int)
    return result


def validate_payload(payload: dict) -> dict:
    # These fields mirror the feature columns expected by the trained pipeline.
    required_fields = [
        "time_of_day",
        "app_category",
        "duration_minutes",
        "is_class_time",
        "is_study_period",
        "is_late_night",
        "hours_to_deadline",
        "task_priority",
        "assignment_count",
        "notification_count",
        "unlock_count",
    ]

    missing = [field for field in required_fields if _first(payload, field) in (None, "")]
    if missing:
        raise ValueError(f"Thiếu dữ liệu: {', '.join(missing)}")

    time_of_day = _first(payload, "time_of_day")
    app_category = _first(payload, "app_category")
    task_priority = _first(payload, "task_priority")

    if time_of_day not in TIME_OF_DAY:
        raise ValueError("time_of_day không hợp lệ.")
    if app_category not in APP_CATEGORIES:
        raise ValueError("app_category không hợp lệ.")
    if task_priority not in TASK_PRIORITIES:
        raise ValueError("task_priority không hợp lệ.")

    today = pd.Timestamp.today().normalize()
    day_of_week = int(today.dayofweek)

    return {
        "time_of_day": time_of_day,
        "app_category": app_category,
        "duration_minutes": _to_int(_first(payload, "duration_minutes"), "duration_minutes", min_value=1),
        "is_class_time": _to_binary(_first(payload, "is_class_time"), "is_class_time"),
        "is_study_period": _to_binary(_first(payload, "is_study_period"), "is_study_period"),
        "is_late_night": _to_binary(_first(payload, "is_late_night"), "is_late_night"),
        "hours_to_deadline": _to_float(_first(payload, "hours_to_deadline"), "hours_to_deadline", min_value=0),
        "task_priority": task_priority,
        "assignment_count": _to_int(_first(payload, "assignment_count"), "assignment_count", min_value=0),
        "notification_count": _to_int(_first(payload, "notification_count"), "notification_count", min_value=0),
        "unlock_count": _to_int(_first(payload, "unlock_count"), "unlock_count", min_value=0),
        "hour": TIME_TO_HOUR[time_of_day],
        "day_of_week": day_of_week,
        "is_weekend": int(day_of_week in (5, 6)),
    }


def _to_binary(value, field_name: str) -> int:
    converted = _to_int(value, field_name, min_value=0)
    if converted not in (0, 1):
        raise ValueError(f"{field_name} chỉ nhận 0 hoặc 1.")
    return converted


def _to_int(value, field_name: str, min_value: int) -> int:
    try:
        converted = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} phải là số nguyên.") from None
    if converted < min_value:
        raise ValueError(f"{field_name} phải >= {min_value}.")
    return converted


def _to_float(value, field_name: str, min_value: float) -> float:
    try:
        converted = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} phải là số.") from None
    if converted < min_value:
        raise ValueError(f"{field_name} phải >= {min_value}.")
    return converted


def build_feature_frame(payload: dict) -> pd.DataFrame:
    cleaned = validate_payload(payload)
    df = pd.DataFrame([cleaned])
    # Keep this order aligned with the training data after timestamp-derived fields are recreated.
    ordered_columns = [
        "time_of_day",
        "app_category",
        "duration_minutes",
        "is_class_time",
        "is_study_period",
        "is_late_night",
        "hours_to_deadline",
        "task_priority",
        "assignment_count",
        "notification_count",
        "unlock_count",
        "hour",
        "day_of_week",
        "is_weekend",
    ]
    return df[ordered_columns]


def build_explanations(payload: dict) -> list[dict]:
    cleaned = validate_payload(payload)
    explanations = []

    if cleaned["app_category"] in DISTRACTING_APPS:
        explanations.append({"tone": "risk", "title": "Ứng dụng dễ gây xao nhãng", "detail": "Bạn đang dùng nhóm app thường liên quan đến giải trí hoặc phân tâm."})
    if cleaned["hours_to_deadline"] < 24:
        explanations.append({"tone": "risk", "title": "Deadline rất gần", "detail": "Công việc còn dưới 24 giờ, nên việc mất tập trung lúc này đáng chú ý hơn."})
    elif cleaned["hours_to_deadline"] < 48:
        explanations.append({"tone": "watch", "title": "Deadline đang đến gần", "detail": "Bạn chỉ còn khoảng 1–2 ngày để xử lý công việc."})
    if cleaned["is_class_time"] == 1:
        explanations.append({"tone": "risk", "title": "Sử dụng trong giờ học", "detail": "Dùng điện thoại ngay trong giờ học là tín hiệu cần lưu ý."})
    if cleaned["is_study_period"] == 1:
        explanations.append({"tone": "watch", "title": "Đang trong khung giờ nên học", "detail": "Phiên sử dụng diễn ra đúng lúc đáng ra nên tập trung cho việc học."})
    if cleaned["is_late_night"] == 1:
        explanations.append({"tone": "watch", "title": "Sử dụng vào đêm muộn", "detail": "Đêm muộn thường làm giảm chất lượng tập trung và tự kiểm soát."})
    if cleaned["duration_minutes"] >= 53:
        explanations.append({"tone": "risk", "title": "Phiên dùng khá dài", "detail": "Thời lượng trên khoảng 45–60 phút làm tăng khả năng bị cuốn vào điện thoại."})
    if cleaned["notification_count"] >= 20:
        explanations.append({"tone": "watch", "title": "Nhiều thông báo", "detail": "Lượng thông báo cao dễ làm đứt mạch tập trung."})
    if cleaned["unlock_count"] >= 8:
        explanations.append({"tone": "watch", "title": "Mở điện thoại nhiều lần", "detail": "Số lần mở máy cao cho thấy mức độ bị kéo trở lại điện thoại khá lớn."})
    if cleaned["task_priority"] == "High":
        explanations.append({"tone": "context", "title": "Nhiệm vụ có ưu tiên cao", "detail": "Công việc quan trọng khiến mọi tín hiệu phân tâm trở nên đáng chú ý hơn."})
    if not explanations:
        explanations.append({"tone": "positive", "title": "Chưa thấy tín hiệu rủi ro nổi bật", "detail": "Các câu trả lời hiện tại không cho thấy yếu tố phân tâm mạnh nào quá rõ."})
    return explanations[:5]


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Không tìm thấy outputs/best_model.joblib. Hãy chạy train_model.py trước.")
    try:
        return joblib.load(MODEL_PATH)
    except AttributeError as exc:
        raise RuntimeError(
            "Không thể load model vì phiên bản thư viện hiện tại khác môi trường đã train model. "
            "Hãy kích hoạt đúng environment rồi chạy lại: python train_model.py"
        ) from exc


def predict(payload: dict, model=None) -> dict:
    model = model or load_model()
    feature_df = build_feature_frame(payload)
    pred_num = int(model.predict(feature_df)[0])
    pred_label = INV_LABEL_MAP[pred_num]

    probabilities = None
    if hasattr(model, "predict_proba"):
        raw_probs = model.predict_proba(feature_df)[0]
        probabilities = {INV_LABEL_MAP[index]: round(float(probability), 4) for index, probability in enumerate(raw_probs)}

    return {
        "label": pred_label,
        "probabilities": probabilities,
        "advice": get_study_advice(pred_label),
        "explanations": build_explanations(payload),
    }


def get_study_advice(label: str) -> str:
    advice_map = {
        "Low": "Bạn đang kiểm soát khá tốt. Hãy duy trì lịch học và nghỉ ngắn có chủ đích.",
        "Medium": "Nên đặt mục tiêu nhỏ trong 25 phút và tắt bớt thông báo trong lúc học.",
        "High": "Hãy bắt đầu bằng một nhiệm vụ rất nhỏ, giới hạn app gây xao nhãng và ưu tiên việc gần deadline.",
    }
    return advice_map[label]
