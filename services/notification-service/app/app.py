from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# In-memory log (notifications don't need persistence for this project)
notifications = []

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "notification-service", "version": "1.0.0"})

@app.route("/api/v1/notifications", methods=["POST"])
def send_notification():
    data = request.json
    if not data or not data.get("to") or not data.get("message"):
        return jsonify({"error": "Fields 'to' and 'message' are required"}), 400

    notification = {
        "id": len(notifications) + 1,
        "to": data.get("to"),
        "message": data.get("message"),
        "type": data.get("type", "email"),
        "status": "sent",
        "sent_at": datetime.utcnow().isoformat()
    }
    notifications.append(notification)
    print(f"[NOTIFICATION] {notification}", flush=True)
    return jsonify(notification), 201

@app.route("/api/v1/notifications", methods=["GET"])
def get_notifications():
    return jsonify(notifications)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005, debug=True)