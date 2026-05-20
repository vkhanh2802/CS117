from flask import Flask, request, jsonify
import os

from prediction_service import predict


# 1. Lay duong dan tuyet doi tu file app.py toi thu muc dist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "student-phone-impact", "dist")

# Khoi tao Flask tro thang vao duong dan tuyet doi do
app = Flask(__name__, static_folder=DIST_DIR, static_url_path="/")


# 2. Route hien thi trang chu
@app.route("/")
def serve_react_app():
    # Bao loi ro rang neu chua build React app.
    if not os.path.exists(os.path.join(DIST_DIR, "index.html")):
        return f"Loi: Khong tim thay file index.html tai {DIST_DIR}. Ban da chay npm run build chua?", 404

    return app.send_static_file("index.html")


# 3. API Du doan
@app.route("/api/predict", methods=["POST"])
def predict_delay():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(predict(payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        app.logger.exception("Prediction failed")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
