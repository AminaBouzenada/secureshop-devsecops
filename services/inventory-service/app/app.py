from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('DB_USER','postgres')}:"
    f"{os.getenv('DB_PASSWORD','postgres')}@"
    f"{os.getenv('DB_HOST','localhost')}:"
    f"{os.getenv('DB_PORT','5432')}/"
    f"{os.getenv('DB_NAME','inventorydb')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Inventory(db.Model):
    __tablename__ = "inventory"
    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, unique=True, nullable=False)
    quantity   = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()
    if Inventory.query.count() == 0:
        for pid, qty in [(1, 100), (2, 50), (3, 75)]:
            db.session.add(Inventory(product_id=pid, quantity=qty))
        db.session.commit()

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "inventory-service", "version": "1.0.0"})

@app.route("/api/v1/inventory", methods=["GET"])
def get_all_inventory():
    items = Inventory.query.all()
    return jsonify([{"product_id": i.product_id, "quantity": i.quantity} for i in items])

@app.route("/api/v1/inventory/<int:product_id>", methods=["GET"])
def get_inventory(product_id):
    inv = Inventory.query.filter_by(product_id=product_id).first_or_404()
    return jsonify({"product_id": inv.product_id, "quantity": inv.quantity})

@app.route("/api/v1/inventory/<int:product_id>", methods=["PUT"])
def update_inventory(product_id):
    inv = Inventory.query.filter_by(product_id=product_id).first()
    if not inv:
        inv = Inventory(product_id=product_id, quantity=0)
        db.session.add(inv)
    data = request.json
    inv.quantity = data.get("quantity", inv.quantity)
    db.session.commit()
    return jsonify({"product_id": inv.product_id, "quantity": inv.quantity})

@app.route("/api/v1/inventory/<int:product_id>/reserve", methods=["POST"])
def reserve_inventory(product_id):
    inv = Inventory.query.filter_by(product_id=product_id).first_or_404()
    quantity = request.json.get("quantity", 1)
    if inv.quantity < quantity:
        return jsonify({"error": "Insufficient stock"}), 400
    inv.quantity -= quantity
    db.session.commit()
    return jsonify({"status": "reserved", "remaining": inv.quantity})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8006, debug=True)