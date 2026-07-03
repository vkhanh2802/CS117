APP_GROUPS = {"Productivity", "Social", "Entertainment", "Gaming", "System"}
TASK_IMPORTANCE = {"Low", "Medium", "High"}
TASK_RELEVANCE = {"Related", "Neutral", "Unrelated"}


def _required(payload: dict, field_name: str):
    value = payload.get(field_name)
    if value in (None, ""):
        raise ValueError(f"Thiếu dữ liệu: {field_name}")
    return value


def _to_int(value, field_name: str, min_value: int = 0) -> int:
    try:
        converted = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} phải là số nguyên.") from None
    if converted < min_value:
        raise ValueError(f"{field_name} phải >= {min_value}.")
    return converted


def _to_float(value, field_name: str, min_value: float = 0.0) -> float:
    try:
        converted = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} phải là số.") from None
    if converted < min_value:
        raise ValueError(f"{field_name} phải >= {min_value}.")
    return converted


def _normalize_threshold(value, field_name: str) -> float:
    threshold = _to_float(value, field_name, min_value=0.0)
    # Accept both 0-1 and 0-100 style input for convenience.
    if threshold > 1:
        threshold = threshold / 100.0
    if threshold < 0 or threshold > 1:
        raise ValueError(f"{field_name} phải nằm trong khoảng 0-1 hoặc 0-100.")
    return threshold


def _normalize_mapping(app_group_mapping: dict) -> dict:
    normalized = {}
    for app_name, group in app_group_mapping.items():
        normalized_app = str(app_name).strip().lower()
        normalized_group = str(group).strip()
        if normalized_group not in APP_GROUPS:
            raise ValueError(f"Nhóm app không hợp lệ cho {app_name}: {group}")
        normalized[normalized_app] = normalized_group
    return normalized


def _infer_app_group(app_name: str, payload: dict, user_config: dict) -> str:
    if payload.get("app_group"):
        group = str(payload["app_group"]).strip()
        if group not in APP_GROUPS:
            raise ValueError("app_group không hợp lệ.")
        return group

    app_group_mapping = user_config.get("app_group_mapping")
    if not isinstance(app_group_mapping, dict) or not app_group_mapping:
        raise ValueError("user_config.app_group_mapping phải là object và không được rỗng.")

    normalized_mapping = _normalize_mapping(app_group_mapping)
    app_key = app_name.strip().lower()
    if app_key not in normalized_mapping:
        raise ValueError("app_name chưa có trong user_config.app_group_mapping.")
    return normalized_mapping[app_key]


def _infer_task_relevance(app_name: str, app_group: str, payload: dict, user_config: dict) -> str:
    explicit = payload.get("task_relevance")
    if explicit:
        value = str(explicit).strip().title()
        if value not in TASK_RELEVANCE:
            raise ValueError("task_relevance phải là Related, Neutral hoặc Unrelated.")
        return value

    app_key = app_name.strip().lower()
    related_apps = {str(item).strip().lower() for item in user_config.get("related_apps", [])}
    neutral_apps = {str(item).strip().lower() for item in user_config.get("neutral_apps", [])}
    related_groups = {str(item).strip() for item in user_config.get("related_groups", [])}
    neutral_groups = {str(item).strip() for item in user_config.get("neutral_groups", [])}

    if app_key in related_apps or app_group in related_groups:
        return "Related"
    if app_key in neutral_apps or app_group in neutral_groups:
        return "Neutral"
    return "Unrelated"


def validate_payload(payload: dict) -> dict:
    app_name = str(_required(payload, "app_name")).strip()
    if not app_name:
        raise ValueError("app_name không được để trống.")

    user_config = payload.get("user_config")
    if not isinstance(user_config, dict):
        raise ValueError("Thiếu dữ liệu: user_config")

    t_low = _normalize_threshold(_required(user_config, "t_low"), "user_config.t_low")
    t_high = _normalize_threshold(_required(user_config, "t_high"), "user_config.t_high")
    if t_low >= t_high:
        raise ValueError("user_config.t_low phải nhỏ hơn user_config.t_high.")

    main_task_description = str(_required(user_config, "main_task_description")).strip()
    if not main_task_description:
        raise ValueError("user_config.main_task_description không được để trống.")

    task_importance = str(_required(payload, "task_importance")).strip().title()
    if task_importance not in TASK_IMPORTANCE:
        raise ValueError("task_importance phải là Low, Medium hoặc High.")

    app_group = _infer_app_group(app_name, payload, user_config)
    task_relevance = _infer_task_relevance(app_name, app_group, payload, user_config)

    return {
        "app_name": app_name,
        "app_group": app_group,
        "app_usage_minutes": _to_float(_required(payload, "app_usage_minutes"), "app_usage_minutes", min_value=0),
        "app_open_count": _to_int(_required(payload, "app_open_count"), "app_open_count", min_value=0),
        "notification_count": _to_int(_required(payload, "notification_count"), "notification_count", min_value=0),
        "hours_to_deadline": _to_float(_required(payload, "hours_to_deadline"), "hours_to_deadline", min_value=0),
        "task_importance": task_importance,
        "pending_tasks_count": _to_int(_required(payload, "pending_tasks_count"), "pending_tasks_count", min_value=0),
        "task_relevance": task_relevance,
        "user_thresholds": {"t_low": t_low, "t_high": t_high},
        "main_task_description": main_task_description,
    }


def _build_factor(name: str, impact: float, detail: str) -> dict:
    return {
        "factor": name,
        "impact": round(impact, 2),
        "detail": detail,
        "tone": "risk" if impact > 0 else "protective",
    }


def _score_risk(cleaned: dict) -> tuple[float, list[dict]]:
    score = 10.0
    factors = []

    group_contrib = {
        "Productivity": -15,
        "Social": 18,
        "Entertainment": 15,
        "Gaming": 22,
        "System": 8,
    }[cleaned["app_group"]]
    score += group_contrib
    factors.append(
        _build_factor(
            "Nhóm ứng dụng hiện tại",
            group_contrib,
            f"Nhóm {cleaned['app_group']} tác động {'tăng' if group_contrib > 0 else 'giảm'} nguy cơ trì hoãn.",
        )
    )

    duration_contrib = min(25.0, cleaned["app_usage_minutes"] * 0.35)
    score += duration_contrib
    factors.append(
        _build_factor(
            "Thời lượng sử dụng ứng dụng",
            duration_contrib,
            f"Dùng app {round(cleaned['app_usage_minutes'], 1)} phút trong phiên học.",
        )
    )

    open_contrib = min(12.0, cleaned["app_open_count"] * 1.2)
    score += open_contrib
    factors.append(
        _build_factor(
            "Số lần mở điện thoại/app",
            open_contrib,
            f"Bạn mở điện thoại hoặc app {cleaned['app_open_count']} lần.",
        )
    )

    notification_contrib = min(15.0, cleaned["notification_count"] * 0.6)
    score += notification_contrib
    factors.append(
        _build_factor(
            "Số thông báo nhận được",
            notification_contrib,
            f"Có {cleaned['notification_count']} thông báo trong phiên học.",
        )
    )

    hours_to_deadline = cleaned["hours_to_deadline"]
    if hours_to_deadline <= 6:
        deadline_contrib = 20
    elif hours_to_deadline <= 24:
        deadline_contrib = 15
    elif hours_to_deadline <= 48:
        deadline_contrib = 10
    elif hours_to_deadline <= 72:
        deadline_contrib = 6
    else:
        deadline_contrib = 2

    score += deadline_contrib
    factors.append(
        _build_factor(
            "Deadline còn lại",
            deadline_contrib,
            f"Deadline còn {round(hours_to_deadline, 1)} giờ.",
        )
    )

    importance_contrib = {"Low": 0, "Medium": 6, "High": 12}[cleaned["task_importance"]]
    score += importance_contrib
    factors.append(
        _build_factor(
            "Mức độ quan trọng nhiệm vụ",
            importance_contrib,
            f"Nhiệm vụ hiện tại được đặt ở mức {cleaned['task_importance']}.",
        )
    )

    pending_tasks_contrib = min(12.0, cleaned["pending_tasks_count"] * 2.0)
    score += pending_tasks_contrib
    factors.append(
        _build_factor(
            "Số đầu việc cần hoàn thành",
            pending_tasks_contrib,
            f"Bạn còn {cleaned['pending_tasks_count']} đầu việc.",
        )
    )

    relevance_contrib = {"Related": -18, "Neutral": 4, "Unrelated": 20}[cleaned["task_relevance"]]
    score += relevance_contrib
    factors.append(
        _build_factor(
            "Độ liên quan với nhiệm vụ chính",
            relevance_contrib,
            f"Hoạt động hiện tại được đánh giá là {cleaned['task_relevance']} với nhiệm vụ chính.",
        )
    )

    if (
        cleaned["task_importance"] == "High"
        and cleaned["hours_to_deadline"] <= 24
        and cleaned["task_relevance"] == "Unrelated"
    ):
        interaction_contrib = 12
        score += interaction_contrib
        factors.append(
            _build_factor(
                "Tổ hợp nguy cơ cao",
                interaction_contrib,
                "Nhiệm vụ quan trọng, deadline gần và hoạt động hiện tại không liên quan.",
            )
        )

    if cleaned["app_group"] == "Productivity" and cleaned["task_relevance"] == "Related":
        protective_contrib = -8
        score += protective_contrib
        factors.append(
            _build_factor(
                "Tín hiệu tập trung tích cực",
                protective_contrib,
                "Bạn đang dùng app năng suất có liên quan trực tiếp đến nhiệm vụ.",
            )
        )

    score = max(0.0, min(100.0, score))
    return score, factors


def _label_from_threshold(probability: float, t_low: float, t_high: float) -> str:
    if probability < t_low:
        return "Low"
    if probability < t_high:
        return "Medium"
    return "High"


def _build_recommendations(cleaned: dict, label: str, top_factors: list[dict]) -> list[str]:
    recommendations = []

    if label == "Low":
        recommendations.append("Bạn đang kiểm soát tốt, tiếp tục học theo block 25-30 phút và nghỉ ngắn 5 phút.")
    elif label == "Medium":
        recommendations.append("Bật chế độ tập trung trong 30 phút và tắt thông báo từ app không liên quan.")
    else:
        recommendations.append("Nguy cơ cao: ưu tiên ngay đầu việc quan trọng nhất trong 15 phút đầu tiên.")

    if cleaned["hours_to_deadline"] <= 24:
        recommendations.append("Deadline đang gần, nên tách nhiệm vụ thành các mốc nhỏ theo giờ.")

    if cleaned["notification_count"] >= 12:
        recommendations.append("Giảm thông báo: bật Do Not Disturb hoặc chỉ giữ thông báo học tập khẩn cấp.")

    if cleaned["task_relevance"] == "Unrelated":
        recommendations.append("App hiện tại không phục vụ nhiệm vụ chính, hãy chuyển sang app thuộc nhóm Related.")

    if cleaned["pending_tasks_count"] >= 4:
        recommendations.append("Bạn còn nhiều đầu việc, nên lập thứ tự ưu tiên theo mức quan trọng và thời hạn.")

    if cleaned["app_open_count"] >= 8:
        recommendations.append("Đặt giới hạn số lần mở app trong phiên học để giảm đứt mạch tập trung.")

    if not recommendations:
        recommendations.append("Duy trì kế hoạch học tập hiện tại và kiểm tra lại sau 1-2 phiên học.")

    # Keep response concise and actionable.
    return recommendations[:4]


def predict(payload: dict) -> dict:
    cleaned = validate_payload(payload)
    score, factors = _score_risk(cleaned)
    probability = score / 100.0
    t_low = cleaned["user_thresholds"]["t_low"]
    t_high = cleaned["user_thresholds"]["t_high"]
    label = _label_from_threshold(probability, t_low, t_high)

    top_factors = sorted(factors, key=lambda item: abs(item["impact"]), reverse=True)[:5]

    return {
        "risk_score": round(score, 2),
        "risk_probability": round(probability, 4),
        "label": label,
        "thresholds_applied": {
            "t_low": round(t_low, 4),
            "t_high": round(t_high, 4),
        },
        "app_group": cleaned["app_group"],
        "task_relevance": cleaned["task_relevance"],
        "main_task_description": cleaned["main_task_description"],
        "key_factors": top_factors,
        "recommendations": _build_recommendations(cleaned, label, top_factors),
    }
