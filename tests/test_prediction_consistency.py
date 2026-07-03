from prediction_service import predict


SAMPLE_PAYLOAD = {
    "app_name": "Instagram",
    "app_usage_minutes": 45,
    "app_open_count": 8,
    "notification_count": 15,
    "hours_to_deadline": 18,
    "task_importance": "High",
    "pending_tasks_count": 5,
    "task_relevance": "Unrelated",
    "user_config": {
        "t_low": 0.35,
        "t_high": 0.70,
        "main_task_description": "On thi cuoi ky",
        "related_groups": ["Productivity"],
        "related_apps": ["VSCode", "Notion"],
        "app_group_mapping": {
            "instagram": "Social",
            "vscode": "Productivity",
        },
    },
}


def test_prediction_returns_expected_contract_fields():
    response = predict(SAMPLE_PAYLOAD)

    assert "risk_score" in response
    assert "risk_probability" in response
    assert "label" in response
    assert "key_factors" in response
    assert "recommendations" in response
    assert response["label"] in {"Low", "Medium", "High"}
    assert len(response["key_factors"]) > 0
    assert len(response["recommendations"]) > 0


def test_thresholds_change_output_label():
    strict_threshold_payload = {
        **SAMPLE_PAYLOAD,
        "user_config": {
            **SAMPLE_PAYLOAD["user_config"],
            "t_low": 0.15,
            "t_high": 0.30,
        },
    }
    loose_threshold_payload = {
        **SAMPLE_PAYLOAD,
        "user_config": {
            **SAMPLE_PAYLOAD["user_config"],
            "t_low": 0.80,
            "t_high": 0.95,
        },
    }

    strict_result = predict(strict_threshold_payload)
    loose_result = predict(loose_threshold_payload)

    assert strict_result["label"] in {"Medium", "High"}
    assert loose_result["label"] in {"Low", "Medium"}


def test_mapping_is_required_when_app_group_not_provided():
    invalid_payload = {
        **SAMPLE_PAYLOAD,
        "app_name": "Unknown App",
    }

    try:
        predict(invalid_payload)
    except ValueError as exc:
        assert "app_group_mapping" in str(exc)
    else:
        raise AssertionError("Thiếu mapping app-group phải bị từ chối.")
