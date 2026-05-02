from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('DB_USER','postgres')}:"
    f"{os.getenv('DB_PASSWORD','postgres')}@"
    f"{os.getenv('DB_HOST','localhost')}:"
    f"{os.getenv('DB_PORT','5432')}/"
    f"{os.getenv('DB_NAME','orderdb')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Order(db.Model):
    __tablename__ = "orders"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, nullable=False)
    items        = db.Column(db.JSON, nullable=False, default=list)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    status       = db.Column(db.String(50), default="pending")
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "order-service", "version": "1.0.0"})

@app.route("/api/v1/orders", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    return jsonify([{
        "id": o.id,
        "user_id": o.user_id,
        "items": o.items,
        "total_amount": o.total_amount,
        "status": o.status,
        "created_at": o.created_at.isoformat()
    } for o in orders])

@app.route("/api/v1/orders", methods=["POST"])
def create_order():
    data = request.json
    order = Order(
        user_id=data.get("user_id"),
        items=data.get("items", []),
        total_amount=data.get("total_amount", 0),
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({
        "id": order.id,
        "user_id": order.user_id,
        "items": order.items,
        "total_amount": order.total_amount,
        "status": order.status
    }), 201

@app.route("/api/v1/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        "id": order.id,
        "user_id": order.user_id,
        "items": order.items,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at.isoformat()
    })

@app.route("/api/v1/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.json
    order.status = data.get("status", order.status)
    db.session.commit()
    return jsonify({"id": order.id, "status": order.status})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003, debug=True)