# FocusGuard AI

Web demo Machine Learning dự đoán mức độ trì hoãn công việc của sinh viên khi sử dụng điện thoại.

## Input/Output Contract (đã đồng bộ backend + web)

API `POST /api/predict` hiện nhận dữ liệu theo đúng nhóm sau:

- Hành vi dùng điện thoại:
	- `app_name`
	- `app_usage_minutes`
	- `app_open_count`
	- `notification_count`
- Ngữ cảnh học tập:
	- `hours_to_deadline`
	- `task_importance` (`Low|Medium|High`)
	- `pending_tasks_count`
- Cấu hình người dùng (`user_config`):
	- `t_low`, `t_high` (chấp nhận dạng `0-1` hoặc `0-100`)
	- `app_group_mapping` (map app -> `Productivity|Social|Entertainment|Gaming|System`)
	- `main_task_description`
	- `related_apps`, `related_groups` (để suy ra task relevance nếu không gửi trực tiếp)
- Mức độ liên quan hoạt động hiện tại:
	- `task_relevance` (`Related|Neutral|Unrelated`) hoặc để backend tự suy ra từ `user_config`

Output trả về:

- `risk_score` (0-100)
- `risk_probability` (0-1)
- `label` (`Low|Medium|High`) theo `t_low` và `t_high`
- `key_factors` (các yếu tố ảnh hưởng chính)
- `recommendations` (gợi ý hỗ trợ phù hợp)
- `thresholds_applied`, `app_group`, `task_relevance`, `main_task_description`

## Chạy local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
python app.py
```

> Quan trọng: file `best_model.joblib` phải được tạo trong **chính environment** dùng để chạy Flask. Scikit-learn không đảm bảo load model giữa các phiên bản khác nhau.

## Kiểm tra môi trường

```bash
python check_environment.py
```

Lệnh này in ra phiên bản package hiện tại và metadata của model đã train (nếu có).

## Deploy Render

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Python version: dùng file `.python-version`
