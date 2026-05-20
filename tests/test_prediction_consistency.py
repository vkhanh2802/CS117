import joblib

from prediction_service import MODEL_PATH, build_feature_frame, predict


SAMPLE_PAYLOAD = {
    "timestamp": "2026-05-07T23:53",
    "time_of_day": "Night",
    "app_category": "Social",
    "duration_minutes": "37",
    "is_class_time": "0",
    "is_study_period": "0",
    "is_late_night": "1",
    "hours_to_deadline": "167.37",
    "task_priority": "Low",
    "assignment_count": "5",
    "notification_count": "18",
    "unlock_count": "6",
}


def test_backend_prediction_matches_direct_model_prediction():
    model = joblib.load(MODEL_PATH)
    direct_prediction = int(model.predict(build_feature_frame(SAMPLE_PAYLOAD))[0])
    service_prediction = predict(SAMPLE_PAYLOAD, model=model)

    expected_label = {0: "Low", 1: "Medium", 2: "High"}[direct_prediction]
    assert service_prediction["label"] == expected_label


def test_time_features_are_recreated_for_web_input():
    df = build_feature_frame(SAMPLE_PAYLOAD)
    assert {"hour", "day_of_week", "is_weekend"}.issubset(df.columns)


def test_invalid_binary_input_is_rejected():
    invalid_payload = {**SAMPLE_PAYLOAD, "is_class_time": "2"}
    try:
        build_feature_frame(invalid_payload)
    except ValueError as exc:
        assert "is_class_time" in str(exc)
    else:
        raise AssertionError("Dữ liệu nhị phân không hợp lệ phải bị từ chối.")
