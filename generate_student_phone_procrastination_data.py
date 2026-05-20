import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


# =========================
# 1. Các hàm hỗ trợ
# =========================

def is_during_class_hours(current_time):
    """
    Giả định giờ học:
    - Thứ 2 đến Thứ 6
    - Sáng: 7h - 11h
    - Chiều: 13h - 17h

    Trả về True/False.
    Có thêm xác suất 70% để dữ liệu tự nhiên hơn.
    """
    weekday = current_time.weekday()  # Monday = 0, Sunday = 6
    hour = current_time.hour

    if weekday < 5:
        if (7 <= hour < 11) or (13 <= hour < 17):
            return random.random() < 0.7

    return False


def is_study_period(current_time):
    """
    Khoảng thời gian sinh viên có khả năng cần học/làm bài.
    Biến này sát với bài toán trì hoãn công việc hơn is_class_time.

    Ngày thường:
    - 8h - 11h
    - 14h - 17h
    - 19h - 22h

    Cuối tuần:
    - 9h - 11h
    - 15h - 17h
    - 19h - 22h
    """
    weekday = current_time.weekday()
    hour = current_time.hour

    if weekday < 5:
        if (8 <= hour < 11) or (14 <= hour < 17) or (19 <= hour < 22):
            return random.random() < 0.75
    else:
        if (9 <= hour < 11) or (15 <= hour < 17) or (19 <= hour < 22):
            return random.random() < 0.45

    return False


def get_time_of_day(current_time):
    """Trích xuất đặc trưng buổi trong ngày."""
    hour = current_time.hour

    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 22:
        return "Evening"
    else:
        return "Night"


def generate_realistic_duration(app_category):
    """
    Sinh thời gian sử dụng app theo phân phối chuẩn.
    Dùng max để tránh sinh ra giá trị âm hoặc quá thấp.
    """
    if app_category == "Gaming":
        return max(5, int(np.random.normal(loc=60, scale=20)))
    elif app_category == "Social":
        return max(2, int(np.random.normal(loc=30, scale=15)))
    elif app_category == "Entertainment":
        return max(5, int(np.random.normal(loc=45, scale=20)))
    elif app_category == "Productivity":
        return max(1, int(np.random.normal(loc=25, scale=10)))
    else:  # System
        return max(1, int(np.random.normal(loc=10, scale=5)))


def choose_app_category(current_time, hours_to_deadline):
    """
    Chọn loại app theo thời điểm để dữ liệu thực tế hơn random đều.

    Ý tưởng:
    - Buổi tối/đêm: dễ dùng Social, Gaming, Entertainment hơn.
    - Gần deadline: Productivity có xác suất cao hơn một chút,
      nhưng vẫn có khả năng sinh viên trì hoãn bằng app giải trí.
    - Trong giờ học: System/Productivity cao hơn, nhưng vẫn có nhiễu.
    """
    time_of_day = get_time_of_day(current_time)
    in_class = is_during_class_hours(current_time)

    if in_class:
        categories = ["Social", "Gaming", "Productivity", "Entertainment", "System"]
        weights = [0.25, 0.10, 0.30, 0.15, 0.20]
    elif hours_to_deadline < 24:
        categories = ["Social", "Gaming", "Productivity", "Entertainment", "System"]
        weights = [0.25, 0.15, 0.35, 0.20, 0.05]
    elif time_of_day == "Night":
        categories = ["Social", "Gaming", "Productivity", "Entertainment", "System"]
        weights = [0.35, 0.25, 0.10, 0.25, 0.05]
    elif time_of_day == "Evening":
        categories = ["Social", "Gaming", "Productivity", "Entertainment", "System"]
        weights = [0.30, 0.25, 0.20, 0.20, 0.05]
    else:
        categories = ["Social", "Gaming", "Productivity", "Entertainment", "System"]
        weights = [0.25, 0.15, 0.30, 0.15, 0.15]

    return random.choices(categories, weights=weights, k=1)[0]


def generate_notification_count(app_category, duration_minutes):
    """
    Sinh số lượng thông báo trong phiên sử dụng.
    Social thường có nhiều thông báo hơn.
    """
    if app_category == "Social":
        base = np.random.normal(loc=18, scale=7)
    elif app_category == "Gaming":
        base = np.random.normal(loc=8, scale=4)
    elif app_category == "Entertainment":
        base = np.random.normal(loc=10, scale=5)
    elif app_category == "Productivity":
        base = np.random.normal(loc=5, scale=3)
    else:
        base = np.random.normal(loc=3, scale=2)

    # Dùng lâu hơn thì có thể nhận nhiều thông báo hơn
    value = base + duration_minutes / 20
    return max(0, int(value))


def generate_unlock_count(duration_minutes):
    """
    Sinh số lần mở điện thoại trong khoảng thời gian đó.
    Dùng lâu hơn thường đi kèm số lần mở máy nhiều hơn.
    """
    value = np.random.normal(loc=duration_minutes / 8, scale=3)
    return max(1, int(value))


# =========================
# 2. Hàm sinh dữ liệu chính
# =========================

def generate_ml_ready_data(num_students=100, days=7, seed=42):
    """
    Sinh dữ liệu cho bài toán:
    Dự đoán mức độ trì hoãn công việc của sinh viên khi sử dụng điện thoại.

    Mỗi dòng dữ liệu tương ứng với một phiên sử dụng điện thoại.

    Label cần dự đoán:
    - procrastination_level: Low / Medium / High

    Cột risk_score_hidden chỉ dùng để debug, khi train mô hình nên drop cột này.
    """
    random.seed(seed)
    np.random.seed(seed)

    data = []

    # Tạo student_id không trùng
    student_ids = random.sample(
        [f"2452{i:04d}" for i in range(1000, 10000)],
        num_students
    )

    for student_id in student_ids:
        start_time = datetime.now() - timedelta(days=days)

        # Mỗi sinh viên có một deadline ngẫu nhiên trong khoảng 3 đến 7 ngày sau thời điểm bắt đầu
        deadline_time = start_time + timedelta(hours=random.randint(72, 168))

        # Số phiên sử dụng điện thoại trong khoảng days ngày
        num_events = random.randint(40 * days, 80 * days)
        current_time = start_time

        for _ in range(num_events):
            current_time += timedelta(minutes=random.randint(10, 180))

            if current_time > start_time + timedelta(days=days):
                break

            hours_to_deadline = max(0, (deadline_time - current_time).total_seconds() / 3600)
            app = choose_app_category(current_time, hours_to_deadline)
            duration = generate_realistic_duration(app)

            in_class = is_during_class_hours(current_time)
            study_period = is_study_period(current_time)
            time_of_day = get_time_of_day(current_time)
            is_late_night = current_time.hour >= 22 or current_time.hour < 5

            # Mức độ quan trọng của công việc
            task_priority = random.choices(
                ["Low", "Medium", "High"],
                weights=[0.25, 0.45, 0.30],
                k=1
            )[0]

            # Số lượng bài tập/công việc đang cần xử lý
            assignment_count = random.randint(0, 5)

            # Số thông báo và số lần mở điện thoại
            notification_count = generate_notification_count(app, duration)
            unlock_count = generate_unlock_count(duration)

            # =========================
            # 3. Logic sinh nhãn
            # =========================
            risk_score = 0

            # App gây xao nhãng
            distracting_apps = ["Gaming", "Social", "Entertainment"]

            # 1. Dùng app giải trí trong giờ học
            if in_class and app in distracting_apps:
                risk_score += 45

            # 2. Dùng app giải trí trong khoảng thời gian nên học/làm việc
            if study_period and app in distracting_apps:
                risk_score += 40

            # 3. Gần deadline nhưng vẫn dùng app gây xao nhãng
            if hours_to_deadline < 48 and app in ["Gaming", "Entertainment"]:
                risk_score += 35
            elif hours_to_deadline < 24 and app == "Social":
                risk_score += 25

            # 4. Công việc quan trọng nhưng dùng app gây xao nhãng
            if task_priority == "High" and app in distracting_apps:
                risk_score += 20
            elif task_priority == "Medium" and app in distracting_apps:
                risk_score += 10

            # 5. Có nhiều bài tập/công việc cần làm
            risk_score += assignment_count * 5

            # 6. Dùng điện thoại khuya
            if is_late_night and app in distracting_apps:
                risk_score += 20

            # 7. Dùng càng lâu thì nguy cơ trì hoãn càng cao
            risk_score += (duration / 60) * 15

            # 8. Thông báo nhiều và mở điện thoại nhiều làm tăng phân tâm
            risk_score += notification_count * 0.5
            risk_score += unlock_count * 1.2

            # 9. App năng suất làm giảm mức độ trì hoãn
            if app == "Productivity":
                risk_score -= 25

            # 10. App hệ thống gần như trung tính
            if app == "System":
                risk_score -= 10

            # 11. Thêm nhiễu để dữ liệu tự nhiên hơn, tránh quá máy móc
            noise = np.random.normal(loc=0, scale=15)
            final_score = risk_score + noise

            # 12. Gán nhãn
            if final_score >= 65:
                procrastination_level = "High"
            elif final_score >= 35:
                procrastination_level = "Medium"
            else:
                procrastination_level = "Low"

            data.append({
                "student_id": student_id,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "time_of_day": time_of_day,
                "app_category": app,
                "duration_minutes": duration,
                "is_class_time": int(in_class),
                "is_study_period": int(study_period),
                "is_late_night": int(is_late_night),
                "hours_to_deadline": round(hours_to_deadline, 2),
                "task_priority": task_priority,
                "assignment_count": assignment_count,
                "notification_count": notification_count,
                "unlock_count": unlock_count,
                "risk_score_hidden": round(final_score, 2),
                "procrastination_level": procrastination_level
            })

    return pd.DataFrame(data)


# =========================
# 4. Chạy sinh dữ liệu và lưu file CSV
# =========================

if __name__ == "__main__":
    print("Đang sinh dữ liệu cho bài toán dự đoán mức độ trì hoãn công việc...")

    df = generate_ml_ready_data(
        num_students=100,
        days=7,
        seed=42
    )

    print("\n--- 5 dòng dữ liệu mẫu ---")
    display_df = df.drop(columns=["risk_score_hidden"])
    print(display_df.head())

    print("\n--- Kích thước dữ liệu ---")
    print(df.shape)

    print("\n--- Phân phối nhãn trì hoãn ---")
    print(df["procrastination_level"].value_counts())

    print("\n--- Tỷ lệ phần trăm nhãn trì hoãn ---")
    print(
        df["procrastination_level"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .astype(str) + "%"
    )

    # File đầy đủ có risk_score_hidden để bạn kiểm tra logic sinh nhãn
    df.to_csv("student_phone_procrastination_full.csv", index=False, encoding="utf-8-sig")

    # File dùng để train ML: bỏ risk_score_hidden
    ml_df = df.drop(columns=["risk_score_hidden"])
    ml_df.to_csv("student_phone_procrastination_ml_ready.csv", index=False, encoding="utf-8-sig")

    print("\nĐã lưu 2 file CSV:")
    print("1. student_phone_procrastination_full.csv")
    print("2. student_phone_procrastination_ml_ready.csv")

    print("\nGợi ý khi train mô hình:")
    print("- Dùng student_phone_procrastination_ml_ready.csv")
    print("- Cột target/label: procrastination_level")
    print("- Không nên dùng risk_score_hidden để train vì đó là điểm nội bộ dùng để sinh nhãn")
