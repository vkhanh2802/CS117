# FocusGuard AI

Web demo Machine Learning dự đoán mức độ trì hoãn công việc của sinh viên khi sử dụng điện thoại.

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
